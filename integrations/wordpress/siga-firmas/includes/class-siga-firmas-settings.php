<?php
/**
 * Página de ajustes del plugin (Ajustes → SIGA Firmas).
 *
 * @package SIGA_Firmas
 */

defined( 'ABSPATH' ) || exit;

/**
 * Registra la página de opciones y los campos de configuración.
 */
class SIGA_Firmas_Settings {

	const PAGE_SLUG  = 'siga-firmas';
	const GROUP      = 'siga_firmas_group';

	/**
	 * Engancha los hooks de administración.
	 */
	public static function init() {
		add_action( 'admin_menu', array( __CLASS__, 'add_menu' ) );
		add_action( 'admin_init', array( __CLASS__, 'register' ) );
		add_filter(
			'plugin_action_links_' . plugin_basename( SIGA_FIRMAS_FILE ),
			array( __CLASS__, 'action_links' )
		);
	}

	/**
	 * Añade el enlace "Ajustes" en la lista de plugins.
	 *
	 * @param string[] $links Enlaces existentes.
	 * @return string[]
	 */
	public static function action_links( $links ) {
		$url = admin_url( 'options-general.php?page=' . self::PAGE_SLUG );
		array_unshift(
			$links,
			'<a href="' . esc_url( $url ) . '">' . esc_html__( 'Ajustes', 'siga-firmas' ) . '</a>'
		);
		return $links;
	}

	/**
	 * Registra la página bajo el menú Ajustes.
	 */
	public static function add_menu() {
		add_options_page(
			__( 'SIGA · Recogida de firmas', 'siga-firmas' ),
			__( 'SIGA Firmas', 'siga-firmas' ),
			'manage_options',
			self::PAGE_SLUG,
			array( __CLASS__, 'render_page' )
		);
	}

	/**
	 * Registra el grupo de opciones con su saneado.
	 */
	public static function register() {
		register_setting(
			self::GROUP,
			SIGA_FIRMAS_OPTION,
			array(
				'type'              => 'array',
				'sanitize_callback' => array( __CLASS__, 'sanitize' ),
				'default'           => siga_firmas_default_settings(),
			)
		);
	}

	/**
	 * Sanea cada campo antes de guardarlo.
	 *
	 * @param array<string,mixed> $input Valores enviados.
	 * @return array<string,string>
	 */
	public static function sanitize( $input ) {
		$input = is_array( $input ) ? $input : array();
		$out   = siga_firmas_default_settings();

		$out['api_url']          = isset( $input['api_url'] ) ? untrailingslashit( esc_url_raw( trim( $input['api_url'] ) ) ) : '';
		$out['actividad_id']     = isset( $input['actividad_id'] ) ? sanitize_text_field( $input['actividad_id'] ) : '';
		$provider                = isset( $input['captcha_provider'] ) ? sanitize_text_field( $input['captcha_provider'] ) : 'turnstile';
		$out['captcha_provider'] = in_array( $provider, array( 'turnstile', 'hcaptcha', 'none' ), true ) ? $provider : 'turnstile';
		$out['captcha_site_key'] = isset( $input['captcha_site_key'] ) ? sanitize_text_field( $input['captcha_site_key'] ) : '';
		$out['terminos_url']     = isset( $input['terminos_url'] ) ? esc_url_raw( trim( $input['terminos_url'] ) ) : '';
		$out['mensaje_exito']    = isset( $input['mensaje_exito'] ) ? sanitize_text_field( $input['mensaje_exito'] ) : '';
		$timeout                 = isset( $input['timeout'] ) ? absint( $input['timeout'] ) : 10;
		$out['timeout']          = (string) min( 60, max( 3, $timeout ) );

		if ( '' !== $out['actividad_id'] && ! self::is_uuid( $out['actividad_id'] ) ) {
			add_settings_error(
				SIGA_FIRMAS_OPTION,
				'actividad_id',
				__( 'El ID de actividad no parece un UUID válido.', 'siga-firmas' ),
				'warning'
			);
		}

		return $out;
	}

	/**
	 * Comprueba si un valor tiene forma de UUID.
	 *
	 * @param string $value Cadena a comprobar.
	 * @return bool
	 */
	public static function is_uuid( $value ) {
		return (bool) preg_match( '/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i', $value );
	}

	/**
	 * Trae de SIGA las actividades de recogida de firmas activas para el
	 * desplegable. Cachea el resultado 5 minutos para no golpear el backend en
	 * cada carga de la página de ajustes.
	 *
	 * @param string $api_url Base del backend (sin barra final).
	 * @param bool   $force   Si true, ignora la caché.
	 * @return array<int,array<string,string>>|WP_Error Lista [{id,nombre,campania}] o error.
	 */
	public static function fetch_actividades( $api_url, $force = false ) {
		$api_url = untrailingslashit( $api_url );
		if ( '' === $api_url ) {
			return new WP_Error( 'no_api', __( 'Falta la URL del backend.', 'siga-firmas' ) );
		}

		$cache_key = 'siga_firmas_actividades_' . md5( $api_url );
		if ( ! $force ) {
			$cached = get_transient( $cache_key );
			if ( is_array( $cached ) ) {
				return $cached;
			}
		}

		$resp = wp_remote_get(
			$api_url . '/api/publico/firmas/actividades',
			array(
				'timeout' => 8,
				'headers' => array( 'Accept' => 'application/json' ),
			)
		);
		if ( is_wp_error( $resp ) ) {
			return $resp;
		}

		$code = (int) wp_remote_retrieve_response_code( $resp );
		if ( $code < 200 || $code >= 300 ) {
			/* translators: %d: código HTTP devuelto por el backend. */
			return new WP_Error( 'http_' . $code, sprintf( __( 'El backend respondió %d.', 'siga-firmas' ), $code ) );
		}

		$body = json_decode( wp_remote_retrieve_body( $resp ), true );
		if ( ! is_array( $body ) ) {
			return new WP_Error( 'bad_json', __( 'Respuesta no válida del backend.', 'siga-firmas' ) );
		}

		$out = array();
		foreach ( $body as $a ) {
			if ( ! is_array( $a ) || empty( $a['id'] ) ) {
				continue;
			}
			$out[] = array(
				'id'       => sanitize_text_field( $a['id'] ),
				'nombre'   => isset( $a['nombre'] ) ? sanitize_text_field( $a['nombre'] ) : sanitize_text_field( $a['id'] ),
				'campania' => isset( $a['campania'] ) && $a['campania'] ? sanitize_text_field( $a['campania'] ) : '',
			);
		}

		set_transient( $cache_key, $out, 5 * MINUTE_IN_SECONDS );
		return $out;
	}

	/**
	 * URL (con nonce) para forzar el refresco de la lista de actividades.
	 *
	 * @return string
	 */
	private static function refresh_url() {
		return wp_nonce_url(
			add_query_arg(
				array(
					'page'         => self::PAGE_SLUG,
					'siga_refresh' => '1',
				),
				admin_url( 'options-general.php' )
			),
			'siga_firmas_refresh'
		);
	}

	/**
	 * Pinta la página de ajustes.
	 */
	public static function render_page() {
		if ( ! current_user_can( 'manage_options' ) ) {
			return;
		}
		$s = siga_firmas_get_settings();

		// ¿Se pidió refrescar la lista de actividades? (enlace con nonce)
		$force_refresh = isset( $_GET['siga_refresh'] ) && check_admin_referer( 'siga_firmas_refresh' );

		// Intento traer las actividades para el desplegable (si hay URL configurada).
		$actividades = '' !== $s['api_url'] ? self::fetch_actividades( $s['api_url'], $force_refresh ) : null;
		?>
		<div class="wrap">
			<h1><?php esc_html_e( 'SIGA · Recogida de firmas', 'siga-firmas' ); ?></h1>
			<p>
				<?php esc_html_e( 'Conecta este sitio con el backend de SIGA. El formulario se inserta con el shortcode:', 'siga-firmas' ); ?>
				<code>[siga_firmas]</code>
				<?php esc_html_e( 'o, indicando otra actividad,', 'siga-firmas' ); ?>
				<code>[siga_firmas actividad="UUID"]</code>
			</p>
			<form action="options.php" method="post">
				<?php settings_fields( self::GROUP ); ?>
				<table class="form-table" role="presentation">
					<tr>
						<th scope="row"><label for="siga_api_url"><?php esc_html_e( 'URL del backend de SIGA', 'siga-firmas' ); ?></label></th>
						<td>
							<input name="<?php echo esc_attr( SIGA_FIRMAS_OPTION ); ?>[api_url]" id="siga_api_url" type="url"
								class="regular-text" placeholder="https://api.tu-dominio.org"
								value="<?php echo esc_attr( $s['api_url'] ); ?>" />
							<p class="description"><?php esc_html_e( 'Base de la API (sin barra final). Se llamará a /api/publico/firmas.', 'siga-firmas' ); ?></p>
						</td>
					</tr>
					<tr>
						<th scope="row"><label for="siga_actividad_id"><?php esc_html_e( 'Actividad de recogida de firmas', 'siga-firmas' ); ?></label></th>
						<td>
						<?php if ( is_array( $actividades ) && ! empty( $actividades ) ) : ?>
							<select name="<?php echo esc_attr( SIGA_FIRMAS_OPTION ); ?>[actividad_id]" id="siga_actividad_id" class="regular-text">
								<option value="">— <?php esc_html_e( 'Selecciona una actividad', 'siga-firmas' ); ?> —</option>
								<?php
								$encontrada = false;
								foreach ( $actividades as $a ) {
									if ( $s['actividad_id'] === $a['id'] ) {
										$encontrada = true;
									}
									$etiqueta = '' !== $a['campania'] ? $a['campania'] . ' — ' . $a['nombre'] : $a['nombre'];
									printf(
										'<option value="%s" %s>%s</option>',
										esc_attr( $a['id'] ),
										selected( $s['actividad_id'], $a['id'], false ),
										esc_html( $etiqueta )
									);
								}
								// Si la actividad guardada ya no está activa, no la perdemos en silencio.
								if ( '' !== $s['actividad_id'] && ! $encontrada ) {
									printf(
										'<option value="%s" selected>%s</option>',
										esc_attr( $s['actividad_id'] ),
										esc_html( $s['actividad_id'] . ' (' . __( 'no activa', 'siga-firmas' ) . ')' )
									);
								}
								?>
							</select>
							<a class="button button-secondary" href="<?php echo esc_url( self::refresh_url() ); ?>"><?php esc_html_e( 'Actualizar actividades', 'siga-firmas' ); ?></a>
							<p class="description"><?php esc_html_e( 'Actividades de recogida de firmas web activas (iniciadas y no cerradas), traídas de SIGA. Se puede sobreescribir por página con el shortcode actividad="…".', 'siga-firmas' ); ?></p>
						<?php elseif ( '' === $s['api_url'] ) : ?>
							<input name="<?php echo esc_attr( SIGA_FIRMAS_OPTION ); ?>[actividad_id]" id="siga_actividad_id" type="text"
								class="regular-text" placeholder="00000000-0000-0000-0000-000000000000"
								value="<?php echo esc_attr( $s['actividad_id'] ); ?>" />
							<p class="description"><?php esc_html_e( 'Guarda primero la URL del backend para elegir la actividad en un desplegable.', 'siga-firmas' ); ?></p>
						<?php else : ?>
							<input name="<?php echo esc_attr( SIGA_FIRMAS_OPTION ); ?>[actividad_id]" id="siga_actividad_id" type="text"
								class="regular-text" placeholder="00000000-0000-0000-0000-000000000000"
								value="<?php echo esc_attr( $s['actividad_id'] ); ?>" />
							<a class="button button-secondary" href="<?php echo esc_url( self::refresh_url() ); ?>"><?php esc_html_e( 'Reintentar', 'siga-firmas' ); ?></a>
							<p class="description" style="color:#b91c1c">
								<?php
								$motivo = is_wp_error( $actividades ) ? $actividades->get_error_message() : __( 'error desconocido', 'siga-firmas' );
								/* translators: %s: motivo del error al contactar con el backend. */
								echo esc_html( sprintf( __( 'No se pudieron cargar las actividades desde SIGA (%s). Introduce el UUID a mano o pulsa «Reintentar».', 'siga-firmas' ), $motivo ) );
								?>
							</p>
						<?php endif; ?>
						</td>
					</tr>
					<tr>
						<th scope="row"><label for="siga_captcha_provider"><?php esc_html_e( 'Proveedor de captcha', 'siga-firmas' ); ?></label></th>
						<td>
							<select name="<?php echo esc_attr( SIGA_FIRMAS_OPTION ); ?>[captcha_provider]" id="siga_captcha_provider">
								<option value="turnstile" <?php selected( $s['captcha_provider'], 'turnstile' ); ?>>Cloudflare Turnstile</option>
								<option value="hcaptcha" <?php selected( $s['captcha_provider'], 'hcaptcha' ); ?>>hCaptcha</option>
								<option value="none" <?php selected( $s['captcha_provider'], 'none' ); ?>><?php esc_html_e( 'Ninguno (solo desarrollo)', 'siga-firmas' ); ?></option>
							</select>
							<p class="description"><?php esc_html_e( 'Debe coincidir con CAPTCHA_PROVIDER del backend. El secreto se configura en SIGA, no aquí.', 'siga-firmas' ); ?></p>
						</td>
					</tr>
					<tr>
						<th scope="row"><label for="siga_captcha_site_key"><?php esc_html_e( 'Clave pública (site key) del captcha', 'siga-firmas' ); ?></label></th>
						<td>
							<input name="<?php echo esc_attr( SIGA_FIRMAS_OPTION ); ?>[captcha_site_key]" id="siga_captcha_site_key" type="text"
								class="regular-text" value="<?php echo esc_attr( $s['captcha_site_key'] ); ?>" />
							<p class="description"><?php esc_html_e( 'Clave pública del widget. La clave secreta NO se guarda en WordPress.', 'siga-firmas' ); ?></p>
						</td>
					</tr>
					<tr>
						<th scope="row"><label for="siga_terminos_url"><?php esc_html_e( 'URL de política de privacidad', 'siga-firmas' ); ?></label></th>
						<td>
							<input name="<?php echo esc_attr( SIGA_FIRMAS_OPTION ); ?>[terminos_url]" id="siga_terminos_url" type="url"
								class="regular-text" value="<?php echo esc_attr( $s['terminos_url'] ); ?>" />
							<p class="description"><?php esc_html_e( 'Se enlaza en la casilla de aceptación de términos.', 'siga-firmas' ); ?></p>
						</td>
					</tr>
					<tr>
						<th scope="row"><label for="siga_mensaje_exito"><?php esc_html_e( 'Mensaje de éxito', 'siga-firmas' ); ?></label></th>
						<td>
							<input name="<?php echo esc_attr( SIGA_FIRMAS_OPTION ); ?>[mensaje_exito]" id="siga_mensaje_exito" type="text"
								class="large-text" value="<?php echo esc_attr( $s['mensaje_exito'] ); ?>" />
							<p class="description"><?php esc_html_e( 'Se muestra cuando SIGA acepta el envío. SIGA también devuelve su propio mensaje.', 'siga-firmas' ); ?></p>
						</td>
					</tr>
					<tr>
						<th scope="row"><label for="siga_timeout"><?php esc_html_e( 'Timeout (segundos)', 'siga-firmas' ); ?></label></th>
						<td>
							<input name="<?php echo esc_attr( SIGA_FIRMAS_OPTION ); ?>[timeout]" id="siga_timeout" type="number" min="3" max="60"
								value="<?php echo esc_attr( $s['timeout'] ); ?>" />
						</td>
					</tr>
				</table>
				<?php submit_button(); ?>
			</form>
		</div>
		<?php
	}
}
