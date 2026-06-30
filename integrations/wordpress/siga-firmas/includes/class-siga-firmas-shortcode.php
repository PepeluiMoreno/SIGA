<?php
/**
 * Shortcode [siga_firmas] que pinta el formulario de recogida de firmas.
 *
 * @package SIGA_Firmas
 */

defined( 'ABSPATH' ) || exit;

/**
 * Registra el shortcode y encola los assets solo cuando se usa.
 */
class SIGA_Firmas_Shortcode {

	const HANDLE = 'siga-firmas';

	/**
	 * Engancha el shortcode.
	 */
	public static function init() {
		add_shortcode( 'siga_firmas', array( __CLASS__, 'render' ) );
	}

	/**
	 * Registra y encola los assets del formulario (CSS, JS y captcha).
	 *
	 * @param array<string,string> $settings Configuración del plugin.
	 */
	private static function enqueue_assets( $settings ) {
		wp_enqueue_style(
			self::HANDLE,
			SIGA_FIRMAS_URL . 'assets/siga-firmas.css',
			array(),
			SIGA_FIRMAS_VERSION
		);

		$deps = array();

		// Script del proveedor de captcha (carga explícita del widget).
		if ( 'turnstile' === $settings['captcha_provider'] && '' !== $settings['captcha_site_key'] ) {
			wp_register_script(
				'cf-turnstile',
				'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit',
				array(),
				null,
				true
			);
			$deps[] = 'cf-turnstile';
		} elseif ( 'hcaptcha' === $settings['captcha_provider'] && '' !== $settings['captcha_site_key'] ) {
			wp_register_script(
				'hcaptcha',
				'https://js.hcaptcha.com/1/api.js?render=explicit',
				array(),
				null,
				true
			);
			$deps[] = 'hcaptcha';
		}

		wp_enqueue_script(
			self::HANDLE,
			SIGA_FIRMAS_URL . 'assets/siga-firmas.js',
			$deps,
			SIGA_FIRMAS_VERSION,
			true
		);

		wp_localize_script(
			self::HANDLE,
			'SIGAFirmas',
			array(
				'restUrl'         => esc_url_raw( rest_url( SIGA_Firmas_Rest::NAMESPACE . SIGA_Firmas_Rest::ROUTE ) ),
				'nonce'           => wp_create_nonce( 'wp_rest' ),
				'captchaProvider' => $settings['captcha_provider'],
				'captchaSiteKey'  => $settings['captcha_site_key'],
				'i18n'            => array(
					'enviando'      => __( 'Enviando…', 'siga-firmas' ),
					'errorGenerico' => __( 'Ha ocurrido un error. Inténtalo de nuevo.', 'siga-firmas' ),
					'captchaFalta'  => __( 'Completa la verificación anti-robot.', 'siga-firmas' ),
				),
			)
		);
	}

	/**
	 * Renderiza el formulario.
	 *
	 * @param array<string,string>|string $atts Atributos del shortcode.
	 * @return string HTML.
	 */
	public static function render( $atts ) {
		$settings = siga_firmas_get_settings();

		$atts = shortcode_atts(
			array(
				'campania'         => $settings['campania_id'],
				'titulo'           => __( 'Firma la campaña', 'siga-firmas' ),
				'boton'            => __( 'Firmar', 'siga-firmas' ),
				'pedir_cp'         => '1', // Mostrar campo código postal.
				'pedir_documento'  => '0', // Mostrar campo documento (DNI/NIE).
			),
			$atts,
			'siga_firmas'
		);

		$campania = sanitize_text_field( $atts['campania'] );

		// Aviso visible solo para administradores si falta configuración.
		if ( '' === $settings['api_url'] || ! SIGA_Firmas_Settings::is_uuid( $campania ) ) {
			if ( current_user_can( 'manage_options' ) ) {
				return '<div class="siga-firmas-aviso">'
					. esc_html__( 'SIGA Firmas: configura la URL del backend y un ID de campaña válido en Ajustes → SIGA Firmas (o en el atributo campania="…").', 'siga-firmas' )
					. '</div>';
			}
			return '';
		}

		self::enqueue_assets( $settings );

		$uid          = 'siga-firmas-' . wp_unique_id();
		$pedir_cp     = '1' === (string) $atts['pedir_cp'];
		$pedir_doc    = '1' === (string) $atts['pedir_documento'];
		$terminos_url = $settings['terminos_url'];

		// Etiqueta de la casilla de términos, con enlace opcional a privacidad.
		if ( '' !== $terminos_url ) {
			$label_terminos = sprintf(
				/* translators: %s: enlace a la política de privacidad. */
				esc_html__( 'He leído y acepto la %s y el tratamiento de mis datos.', 'siga-firmas' ),
				'<a href="' . esc_url( $terminos_url ) . '" target="_blank" rel="noopener">' . esc_html__( 'política de privacidad', 'siga-firmas' ) . '</a>'
			);
		} else {
			$label_terminos = esc_html__( 'Acepto el tratamiento de mis datos conforme a la política de privacidad.', 'siga-firmas' );
		}

		ob_start();
		?>
		<form class="siga-firmas-form" id="<?php echo esc_attr( $uid ); ?>"
			data-campania="<?php echo esc_attr( $campania ); ?>" novalidate>

			<h3 class="siga-firmas-titulo"><?php echo esc_html( $atts['titulo'] ); ?></h3>

			<div class="siga-firmas-row">
				<label class="siga-firmas-field">
					<span><?php esc_html_e( 'Nombre', 'siga-firmas' ); ?> <em>*</em></span>
					<input type="text" name="nombre" maxlength="100" autocomplete="given-name" required />
				</label>
				<label class="siga-firmas-field">
					<span><?php esc_html_e( 'Apellidos', 'siga-firmas' ); ?> <em>*</em></span>
					<input type="text" name="apellidos" maxlength="200" autocomplete="family-name" required />
				</label>
			</div>

			<label class="siga-firmas-field">
				<span><?php esc_html_e( 'Correo electrónico', 'siga-firmas' ); ?> <em>*</em></span>
				<input type="email" name="email" maxlength="200" autocomplete="email" required />
			</label>

			<?php if ( $pedir_cp ) : ?>
			<label class="siga-firmas-field siga-firmas-field--narrow">
				<span><?php esc_html_e( 'Código postal', 'siga-firmas' ); ?></span>
				<input type="text" name="codigo_postal" maxlength="20" autocomplete="postal-code" inputmode="numeric" />
			</label>
			<?php endif; ?>

			<?php if ( $pedir_doc ) : ?>
			<div class="siga-firmas-row">
				<label class="siga-firmas-field siga-firmas-field--narrow">
					<span><?php esc_html_e( 'Tipo de documento', 'siga-firmas' ); ?></span>
					<select name="tipo_documento">
						<option value="DNI">DNI</option>
						<option value="NIE">NIE</option>
						<option value="PASAPORTE"><?php esc_html_e( 'Pasaporte', 'siga-firmas' ); ?></option>
					</select>
				</label>
				<label class="siga-firmas-field">
					<span><?php esc_html_e( 'Número de documento', 'siga-firmas' ); ?></span>
					<input type="text" name="documento" maxlength="255" autocomplete="off" />
				</label>
			</div>
			<?php endif; ?>

			<label class="siga-firmas-check">
				<input type="checkbox" name="acepta_terminos" value="1" required />
				<span><?php echo wp_kses_post( $label_terminos ); ?> <em>*</em></span>
			</label>

			<label class="siga-firmas-check">
				<input type="checkbox" name="acepta_comunicaciones" value="1" />
				<span><?php esc_html_e( 'Quiero recibir información sobre esta y futuras campañas.', 'siga-firmas' ); ?></span>
			</label>

			<?php // Honeypot anti-bots: oculto a humanos, debe quedar vacío. ?>
			<div class="siga-firmas-hp" aria-hidden="true">
				<label><?php esc_html_e( 'No rellenar', 'siga-firmas' ); ?>
					<input type="text" name="website" tabindex="-1" autocomplete="off" />
				</label>
			</div>

			<?php if ( 'none' !== $settings['captcha_provider'] && '' !== $settings['captcha_site_key'] ) : ?>
			<div class="siga-firmas-captcha" data-sitekey="<?php echo esc_attr( $settings['captcha_site_key'] ); ?>"></div>
			<?php endif; ?>

			<button type="submit" class="siga-firmas-submit"><?php echo esc_html( $atts['boton'] ); ?></button>

			<p class="siga-firmas-msg" role="status" aria-live="polite"></p>
		</form>
		<?php
		return ob_get_clean();
	}
}
