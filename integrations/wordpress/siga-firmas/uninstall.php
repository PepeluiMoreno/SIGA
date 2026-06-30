<?php
/**
 * Limpieza al desinstalar el plugin: borra la opción de configuración.
 *
 * @package SIGA_Firmas
 */

defined( 'WP_UNINSTALL_PLUGIN' ) || exit;

delete_option( 'siga_firmas_settings' );
