<?php
/**
 * Endpoint REST de WordPress que recibe el formulario y lo reenvía a SIGA.
 *
 * Ruta: POST /wp-json/siga-firmas/v1/firmar
 *
 * El navegador NO llama directamente a SIGA: envía aquí (mismo origen, con
 * nonce) y WordPress reenvía server-side a /api/publico/firmas. Así evitamos
 * CORS y pasamos la IP real del visitante para que el rate-limit de SIGA
 * funcione. El captcha se resuelve en SIGA con su clave secreta.
 *
 * @package SIGA_Firmas
 */

defined( 'ABSPATH' ) || exit;

/**
 * Registra y atiende la ruta REST de envío de firmas.
 */
class SIGA_Firmas_Rest {

	const NAMESPACE = 'siga-firmas/v1';
	const ROUTE     = '/firmar';

	/**
	 * Engancha el registro de rutas.
	 */
	public static function init() {
		add_action( 'rest_api_init', array( __CLASS__, 'register_routes' ) );
	}

	/**
	 * Declara la ruta REST.
	 */
	public static function register_routes() {
		register_rest_route(
			self::NAMESPACE,
			self::ROUTE,
			array(
				'methods'             => 'POST',
				'callback'            => array( __CLASS__, 'handle' ),
				'permission_callback' => '__return_true', // Público: lo firman visitantes anónimos.
			)
		);
	}

	/**
	 * Procesa el envío: valida, construye el payload y reenvía a SIGA.
	 *
	 * @param WP_REST_Request $request Petición REST.
	 * @return WP_REST_Response
	 */
	public static function handle( WP_REST_Request $request ) {
		$settings = siga_firmas_get_settings();

		// 1. Nonce (defensa CSRF; el captcha y el rate-limit reales están en SIGA).
		$nonce = $request->get_header( 'X-WP-Nonce' );
		if ( ! $nonce || ! wp_verify_nonce( $nonce, 'wp_rest' ) ) {
			return self::error( 403, __( 'Sesión caducada. Recarga la página e inténtalo de nuevo.', 'siga-firmas' ) );
		}

		// 2. Configuración mínima.
		if ( empty( $settings['api_url'] ) ) {
			return self::error( 500, __( 'El formulario no está configurado (falta la URL del backend).', 'siga-firmas' ) );
		}

		$campania_id = $request->get_param( 'campania_id' );
		$campania_id = is_string( $campania_id ) ? trim( $campania_id ) : '';
		if ( '' === $campania_id ) {
			$campania_id = $settings['campania_id'];
		}
		if ( ! SIGA_Firmas_Settings::is_uuid( $campania_id ) ) {
			return self::error( 422, __( 'Campaña no válida.', 'siga-firmas' ) );
		}

		// 3. Honeypot: si viene relleno, fingimos éxito y no llamamos a SIGA.
		$honeypot = (string) $request->get_param( 'website' );
		if ( '' !== trim( $honeypot ) ) {
			return self::ok( array( 'estado' => 'pendiente_verificacion', 'mensaje' => $settings['mensaje_exito'] ) );
		}

		// 4. Validación de campos obligatorios.
		$nombre    = sanitize_text_field( (string) $request->get_param( 'nombre' ) );
		$apellidos = sanitize_text_field( (string) $request->get_param( 'apellidos' ) );
		$email     = sanitize_email( (string) $request->get_param( 'email' ) );
		$acepta    = self::to_bool( $request->get_param( 'acepta_terminos' ) );

		if ( '' === $nombre || '' === $apellidos ) {
			return self::error( 422, __( 'Indica tu nombre y tus apellidos.', 'siga-firmas' ) );
		}
		if ( ! is_email( $email ) ) {
			return self::error( 422, __( 'El correo electrónico no es válido.', 'siga-firmas' ) );
		}
		if ( ! $acepta ) {
			return self::error( 422, __( 'Debes aceptar los términos para firmar.', 'siga-firmas' ) );
		}

		// 5. Construcción del payload para SIGA (FirmaPublicaIn).
		$payload = array(
			'campania_id'          => $campania_id,
			'nombre'               => mb_substr( $nombre, 0, 100 ),
			'apellidos'            => mb_substr( $apellidos, 0, 200 ),
			'email'                => $email,
			'acepta_terminos'      => true,
			'acepta_comunicaciones' => self::to_bool( $request->get_param( 'acepta_comunicaciones' ) ),
			'captcha_token'        => (string) $request->get_param( 'captcha_token' ),
			'website'              => '', // Honeypot ya filtrado; lo enviamos vacío.
		);

		$cp = sanitize_text_field( (string) $request->get_param( 'codigo_postal' ) );
		if ( '' !== $cp ) {
			$payload['codigo_postal'] = mb_substr( $cp, 0, 20 );
		}
		$doc = sanitize_text_field( (string) $request->get_param( 'documento' ) );
		if ( '' !== $doc ) {
			$payload['documento']      = mb_substr( $doc, 0, 255 );
			$tipo_doc                  = sanitize_text_field( (string) $request->get_param( 'tipo_documento' ) );
			$payload['tipo_documento'] = '' !== $tipo_doc ? mb_substr( $tipo_doc, 0, 20 ) : 'DNI';
		}

		// 6. Reenvío a SIGA.
		$url = $settings['api_url'] . '/api/publico/firmas';
		$resp = wp_remote_post(
			$url,
			array(
				'timeout'  => (int) $settings['timeout'],
				'headers'  => array(
					'Content-Type'    => 'application/json',
					'Accept'          => 'application/json',
					// IP real del visitante para el rate-limit por IP de SIGA.
					'X-Forwarded-For' => self::client_ip(),
				),
				'body'     => wp_json_encode( $payload ),
			)
		);

		if ( is_wp_error( $resp ) ) {
			return self::error(
				502,
				__( 'No se pudo contactar con el servidor. Inténtalo de nuevo en unos minutos.', 'siga-firmas' )
			);
		}

		$code = (int) wp_remote_retrieve_response_code( $resp );
		$body = json_decode( wp_remote_retrieve_body( $resp ), true );
		$mensaje = is_array( $body ) && ! empty( $body['mensaje'] )
			? sanitize_text_field( $body['mensaje'] )
			: '';

		if ( $code >= 200 && $code < 300 ) {
			return self::ok(
				array(
					'estado'  => is_array( $body ) && isset( $body['estado'] ) ? sanitize_text_field( $body['estado'] ) : 'ok',
					'mensaje' => '' !== $mensaje ? $mensaje : $settings['mensaje_exito'],
				)
			);
		}

		// SIGA devuelve el motivo en `detail` (HTTPException) o `mensaje`.
		$detalle = '';
		if ( is_array( $body ) ) {
			if ( ! empty( $body['detail'] ) && is_string( $body['detail'] ) ) {
				$detalle = sanitize_text_field( $body['detail'] );
			} elseif ( '' !== $mensaje ) {
				$detalle = $mensaje;
			}
		}
		if ( '' === $detalle ) {
			$detalle = 429 === $code
				? __( 'Demasiados intentos. Inténtalo más tarde.', 'siga-firmas' )
				: __( 'No se pudo registrar la firma. Revisa los datos e inténtalo de nuevo.', 'siga-firmas' );
		}

		return self::error( $code >= 400 && $code < 600 ? $code : 502, $detalle );
	}

	/**
	 * Normaliza valores "truthy" de un formulario a booleano.
	 *
	 * @param mixed $value Valor recibido.
	 * @return bool
	 */
	private static function to_bool( $value ) {
		return in_array( $value, array( true, 1, '1', 'true', 'on', 'yes', 'si' ), true );
	}

	/**
	 * Mejor estimación de la IP del visitante (respeta proxys conocidos de WP).
	 *
	 * @return string
	 */
	private static function client_ip() {
		$candidatos = array( 'HTTP_CF_CONNECTING_IP', 'HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR' );
		foreach ( $candidatos as $key ) {
			if ( empty( $_SERVER[ $key ] ) ) {
				continue;
			}
			$raw = sanitize_text_field( wp_unslash( $_SERVER[ $key ] ) );
			$ip  = trim( explode( ',', $raw )[0] );
			if ( filter_var( $ip, FILTER_VALIDATE_IP ) ) {
				return $ip;
			}
		}
		return '0.0.0.0';
	}

	/**
	 * Respuesta de éxito.
	 *
	 * @param array<string,string> $data Datos.
	 * @return WP_REST_Response
	 */
	private static function ok( $data ) {
		return new WP_REST_Response( array_merge( array( 'ok' => true ), $data ), 200 );
	}

	/**
	 * Respuesta de error con mensaje legible.
	 *
	 * @param int    $code    Código HTTP.
	 * @param string $mensaje Mensaje para el usuario.
	 * @return WP_REST_Response
	 */
	private static function error( $code, $mensaje ) {
		return new WP_REST_Response(
			array(
				'ok'      => false,
				'mensaje' => $mensaje,
			),
			$code
		);
	}
}
