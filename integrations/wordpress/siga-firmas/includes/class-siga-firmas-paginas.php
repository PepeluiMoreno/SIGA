<?php
/**
 * Generador de páginas de campaña de recogida de firmas.
 *
 * Pantalla de administración (Ajustes → Páginas de firmas) que lista las
 * actividades de recogida de firmas activas de SIGA y, por cada una, permite
 * **crear o actualizar** una página de WordPress con la página pública de la
 * recogida: título, lema, imagen, manifiesto, destinatario, el formulario
 * `[siga_firmas actividad="UUID"]`, aviso RGPD y PDF de hoja en papel.
 *
 * SIGA es la fuente única: el contenido se toma de la actividad/campaña
 * (endpoint público GET /api/publico/firmas/pagina/{actividad_id}); WordPress
 * solo materializa la página. El mapa actividad_id → post_id se guarda en una
 * opción para no duplicar (idempotente: crea la primera vez, actualiza después).
 *
 * @package SIGA_Firmas
 */

defined( 'ABSPATH' ) || exit;

/**
 * Pantalla de admin + acción de generación de páginas.
 */
class SIGA_Firmas_Paginas {

	const PAGE_SLUG   = 'siga-firmas-paginas';
	const OPTION_MAP  = 'siga_firmas_paginas';   // actividad_id => post_id
	const ACTION      = 'siga_firmas_crear_pagina';

	/**
	 * Engancha menú y manejador.
	 */
	public static function init() {
		add_action( 'admin_menu', array( __CLASS__, 'add_menu' ) );
		add_action( 'admin_post_' . self::ACTION, array( __CLASS__, 'handle' ) );
	}

	/**
	 * Submenú bajo Ajustes.
	 */
	public static function add_menu() {
		add_options_page(
			__( 'SIGA · Páginas de firmas', 'siga-firmas' ),
			__( 'SIGA Firmas · Páginas', 'siga-firmas' ),
			'manage_options',
			self::PAGE_SLUG,
			array( __CLASS__, 'render_page' )
		);
	}

	/**
	 * Mapa actividad_id → post_id.
	 *
	 * @return array<string,int>
	 */
	private static function mapa() {
		$m = get_option( self::OPTION_MAP, array() );
		return is_array( $m ) ? $m : array();
	}

	/**
	 * Pinta la pantalla: lista de actividades + botón por fila.
	 */
	public static function render_page() {
		if ( ! current_user_can( 'manage_options' ) ) {
			return;
		}
		$settings    = siga_firmas_get_settings();
		$actividades = '' !== $settings['api_url'] ? SIGA_Firmas_Settings::fetch_actividades( $settings['api_url'] ) : null;
		$mapa        = self::mapa();
		?>
		<div class="wrap">
			<h1><?php esc_html_e( 'SIGA · Páginas de recogida de firmas', 'siga-firmas' ); ?></h1>
			<p><?php esc_html_e( 'Genera la página de cada campaña de firmas con el formulario ya incrustado. El contenido se toma de SIGA (fuente única).', 'siga-firmas' ); ?></p>

			<?php
			$aviso = isset( $_GET['siga_pagina'] ) ? sanitize_key( wp_unslash( $_GET['siga_pagina'] ) ) : ''; // phpcs:ignore WordPress.Security.NonceVerification.Recommended
			if ( 'ok' === $aviso ) : ?>
				<div class="notice notice-success is-dismissible"><p><?php esc_html_e( 'Página creada/actualizada como borrador. Revísala y publícala desde WordPress.', 'siga-firmas' ); ?></p></div>
			<?php elseif ( 'error' === $aviso ) : ?>
				<div class="notice notice-error is-dismissible"><p><?php esc_html_e( 'No se pudo generar la página. Revisa la URL del backend y que la actividad exista.', 'siga-firmas' ); ?></p></div>
			<?php endif; ?>

			<?php if ( '' === $settings['api_url'] ) : ?>
				<div class="notice notice-warning"><p><?php esc_html_e( 'Configura primero la URL del backend en Ajustes → SIGA Firmas.', 'siga-firmas' ); ?></p></div>
			<?php elseif ( is_wp_error( $actividades ) ) : ?>
				<div class="notice notice-error"><p><?php echo esc_html( $actividades->get_error_message() ); ?></p></div>
			<?php elseif ( empty( $actividades ) ) : ?>
				<p><?php esc_html_e( 'No hay actividades de recogida de firmas activas.', 'siga-firmas' ); ?></p>
			<?php else : ?>
				<table class="widefat striped">
					<thead><tr>
						<th><?php esc_html_e( 'Actividad', 'siga-firmas' ); ?></th>
						<th><?php esc_html_e( 'Campaña', 'siga-firmas' ); ?></th>
						<th><?php esc_html_e( 'Página', 'siga-firmas' ); ?></th>
						<th></th>
					</tr></thead>
					<tbody>
					<?php foreach ( $actividades as $a ) :
						$post_id  = isset( $mapa[ $a['id'] ] ) ? (int) $mapa[ $a['id'] ] : 0;
						$post_ok  = $post_id && 'trash' !== get_post_status( $post_id );
						?>
						<tr>
							<td><strong><?php echo esc_html( $a['nombre'] ); ?></strong></td>
							<td><?php echo esc_html( $a['campania'] ?? '' ); ?></td>
							<td>
								<?php if ( $post_ok ) : ?>
									<a href="<?php echo esc_url( get_permalink( $post_id ) ); ?>" target="_blank" rel="noopener"><?php esc_html_e( 'Ver', 'siga-firmas' ); ?></a> ·
									<a href="<?php echo esc_url( get_edit_post_link( $post_id ) ); ?>"><?php esc_html_e( 'Editar', 'siga-firmas' ); ?></a>
								<?php else : ?>
									<span class="description"><?php esc_html_e( 'sin página', 'siga-firmas' ); ?></span>
								<?php endif; ?>
							</td>
							<td>
								<form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
									<?php wp_nonce_field( self::ACTION ); ?>
									<input type="hidden" name="action" value="<?php echo esc_attr( self::ACTION ); ?>" />
									<input type="hidden" name="actividad_id" value="<?php echo esc_attr( $a['id'] ); ?>" />
									<button type="submit" class="button button-primary">
										<?php echo $post_ok ? esc_html__( 'Actualizar página', 'siga-firmas' ) : esc_html__( 'Crear página', 'siga-firmas' ); ?>
									</button>
								</form>
							</td>
						</tr>
					<?php endforeach; ?>
					</tbody>
				</table>
			<?php endif; ?>
		</div>
		<?php
	}

	/**
	 * Crea o actualiza la página de una actividad.
	 */
	public static function handle() {
		if ( ! current_user_can( 'manage_options' ) ) {
			wp_die( esc_html__( 'No autorizado.', 'siga-firmas' ) );
		}
		check_admin_referer( self::ACTION );

		$actividad_id = isset( $_POST['actividad_id'] ) ? sanitize_text_field( wp_unslash( $_POST['actividad_id'] ) ) : '';
		$settings     = siga_firmas_get_settings();

		if ( ! SIGA_Firmas_Settings::is_uuid( $actividad_id ) || '' === $settings['api_url'] ) {
			self::redirigir( 'error' );
		}

		$contenido = self::fetch_contenido( $settings['api_url'], $actividad_id );
		if ( is_wp_error( $contenido ) ) {
			self::redirigir( 'error' );
		}

		$mapa    = self::mapa();
		$post_id = isset( $mapa[ $actividad_id ] ) ? (int) $mapa[ $actividad_id ] : 0;

		$postarr = array(
			'post_title'   => '' !== $contenido['titulo'] ? $contenido['titulo'] : __( 'Recogida de firmas', 'siga-firmas' ),
			'post_content' => self::plantilla( $contenido, $actividad_id ),
			'post_type'    => 'page',
			'post_status'  => 'draft',  // se publica desde WP tras revisar
		);

		if ( $post_id && 'trash' !== get_post_status( $post_id ) ) {
			$postarr['ID'] = $post_id;
			$res           = wp_update_post( $postarr, true );
		} else {
			$res = wp_insert_post( $postarr, true );
		}

		if ( is_wp_error( $res ) || ! $res ) {
			self::redirigir( 'error' );
		}

		$mapa[ $actividad_id ] = (int) $res;
		update_option( self::OPTION_MAP, $mapa );
		self::redirigir( 'ok' );
	}

	/**
	 * Trae el contenido de la página desde SIGA.
	 *
	 * @param string $api_url      Base del backend.
	 * @param string $actividad_id UUID.
	 * @return array<string,mixed>|WP_Error
	 */
	private static function fetch_contenido( $api_url, $actividad_id ) {
		$url  = untrailingslashit( $api_url ) . '/api/publico/firmas/pagina/' . rawurlencode( $actividad_id );
		$resp = wp_remote_get( $url, array( 'timeout' => 10, 'headers' => array( 'Accept' => 'application/json' ) ) );
		if ( is_wp_error( $resp ) ) {
			return $resp;
		}
		if ( 200 !== (int) wp_remote_retrieve_response_code( $resp ) ) {
			return new WP_Error( 'http', __( 'El backend no devolvió el contenido.', 'siga-firmas' ) );
		}
		$body = json_decode( wp_remote_retrieve_body( $resp ), true );
		if ( ! is_array( $body ) ) {
			return new WP_Error( 'json', __( 'Respuesta no válida.', 'siga-firmas' ) );
		}
		// Normaliza claves esperadas.
		$out = array();
		foreach ( array( 'titulo', 'lema', 'descripcion', 'imagen_url', 'destinatario', 'manifiesto', 'aviso_rgpd', 'hoja_firmas_url', 'comparte_texto' ) as $k ) {
			$out[ $k ] = isset( $body[ $k ] ) && null !== $body[ $k ] ? (string) $body[ $k ] : '';
		}
		return $out;
	}

	/**
	 * Construye el contenido HTML de la página (bloques clásicos).
	 *
	 * @param array<string,mixed> $c            Contenido de la página.
	 * @param string              $actividad_id UUID de la actividad.
	 * @return string
	 */
	private static function plantilla( $c, $actividad_id ) {
		$html = '';

		if ( '' !== $c['imagen_url'] ) {
			$html .= '<figure class="wp-block-image size-large"><img src="' . esc_url( $c['imagen_url'] ) . '" alt="' . esc_attr( $c['titulo'] ) . '"/></figure>' . "\n\n";
		}
		if ( '' !== $c['lema'] ) {
			$html .= '<p class="has-text-align-center"><strong>' . esc_html( $c['lema'] ) . '</strong></p>' . "\n\n";
		}
		if ( '' !== $c['descripcion'] ) {
			$html .= wp_kses_post( wpautop( $c['descripcion'] ) ) . "\n\n";
		}
		if ( '' !== $c['manifiesto'] ) {
			$html .= '<h2>' . esc_html__( 'Manifiesto', 'siga-firmas' ) . '</h2>' . "\n";
			$html .= wp_kses_post( wpautop( $c['manifiesto'] ) ) . "\n\n";
		}
		if ( '' !== $c['destinatario'] ) {
			$html .= '<p><em>' . esc_html__( 'Dirigido a:', 'siga-firmas' ) . '</em> ' . esc_html( $c['destinatario'] ) . '</p>' . "\n\n";
		}

		// El formulario de firma (shortcode del propio plugin).
		$html .= '[siga_firmas actividad="' . esc_attr( $actividad_id ) . '"]' . "\n\n";

		if ( '' !== $c['hoja_firmas_url'] ) {
			$html .= '<p><a href="' . esc_url( $c['hoja_firmas_url'] ) . '" target="_blank" rel="noopener">' . esc_html__( 'Descargar hoja de firmas (PDF)', 'siga-firmas' ) . '</a></p>' . "\n\n";
		}
		if ( '' !== $c['aviso_rgpd'] ) {
			$html .= '<h3>' . esc_html__( 'Aviso legal y protección de datos', 'siga-firmas' ) . '</h3>' . "\n";
			$html .= '<p class="has-small-font-size">' . esc_html( $c['aviso_rgpd'] ) . '</p>' . "\n";
		}

		return $html;
	}

	/**
	 * Redirige a la pantalla con un aviso.
	 *
	 * @param string $estado ok|error
	 */
	private static function redirigir( $estado ) {
		$url = add_query_arg(
			array( 'page' => self::PAGE_SLUG, 'siga_pagina' => $estado ),
			admin_url( 'options-general.php' )
		);
		wp_safe_redirect( $url );
		exit;
	}
}
