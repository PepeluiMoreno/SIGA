<?php
/**
 * Plugin Name:       SIGA · Recogida de firmas
 * Plugin URI:        https://github.com/PepeluiMoreno/SIGA
 * Description:        Muestra un formulario para recoger los datos de contacto de simpatizantes que firman una campaña y los reenvía al backend de SIGA (endpoint público /api/publico/firmas, doble opt-in). WordPress solo presenta el formulario; SIGA es la fuente única de datos y consentimiento.
 * Version:           1.2.0
 * Requires at least: 5.8
 * Requires PHP:      7.4
 * Author:            SIGA
 * License:           MIT
 * License URI:       https://opensource.org/licenses/MIT
 * Text Domain:       siga-firmas
 * Domain Path:       /languages
 *
 * @package SIGA_Firmas
 */

defined( 'ABSPATH' ) || exit;

define( 'SIGA_FIRMAS_VERSION', '1.2.0' );
define( 'SIGA_FIRMAS_FILE', __FILE__ );
define( 'SIGA_FIRMAS_DIR', plugin_dir_path( __FILE__ ) );
define( 'SIGA_FIRMAS_URL', plugin_dir_url( __FILE__ ) );

/** Clave de la opción donde se guarda toda la configuración del plugin. */
define( 'SIGA_FIRMAS_OPTION', 'siga_firmas_settings' );

require_once SIGA_FIRMAS_DIR . 'includes/class-siga-firmas-settings.php';
require_once SIGA_FIRMAS_DIR . 'includes/class-siga-firmas-rest.php';
require_once SIGA_FIRMAS_DIR . 'includes/class-siga-firmas-shortcode.php';

/**
 * Arranque del plugin: registra ajustes, endpoint REST y shortcode.
 */
function siga_firmas_bootstrap() {
	SIGA_Firmas_Settings::init();
	SIGA_Firmas_Rest::init();
	SIGA_Firmas_Shortcode::init();
}
add_action( 'plugins_loaded', 'siga_firmas_bootstrap' );

/**
 * Valores por defecto de la configuración. Se usan como base y como
 * semilla en la activación.
 *
 * @return array<string,string>
 */
function siga_firmas_default_settings() {
	return array(
		'api_url'          => '',          // Ej: https://api.laicismo.org (sin barra final).
		'actividad_id'     => '',          // UUID de la actividad de recogida de firmas por defecto.
		'captcha_provider' => 'turnstile', // turnstile | hcaptcha | none.
		'captcha_site_key' => '',          // Clave PÚBLICA del captcha (el secreto vive en SIGA).
		'terminos_url'     => '',          // URL de la política de privacidad / términos.
		'mensaje_exito'    => __( 'Gracias. Revisa tu correo para confirmar tu firma.', 'siga-firmas' ),
		'timeout'          => '10',        // Timeout (segundos) de la llamada a SIGA.
	);
}

/**
 * Devuelve la configuración fusionada con los valores por defecto.
 *
 * @return array<string,string>
 */
function siga_firmas_get_settings() {
	$saved = get_option( SIGA_FIRMAS_OPTION, array() );
	if ( ! is_array( $saved ) ) {
		$saved = array();
	}
	return wp_parse_args( $saved, siga_firmas_default_settings() );
}

register_activation_hook(
	__FILE__,
	function () {
		if ( false === get_option( SIGA_FIRMAS_OPTION, false ) ) {
			add_option( SIGA_FIRMAS_OPTION, siga_firmas_default_settings() );
		}
	}
);
