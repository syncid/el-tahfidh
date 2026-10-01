<?php
/**
 * Plugin Name:       My Custom App
 * Description:       Logika bisnis inti situs (OOP, PSR-4, MVC).
 * Version:           0.1.0
 * Requires at least: 6.2
 * Requires PHP:      8.1
 * License:           GPL-2.0-or-later
 * Text Domain:       my-custom-app
 *
 * File ini hanya berisi pengecekan lingkungan dan inisialisasi.
 * Sintaksnya sengaja tetap kompatibel dengan PHP lama agar pesan
 * "PHP terlalu lama" bisa tampil alih-alih fatal parse error.
 */

declare(strict_types=1);

namespace MyCustomApp;

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Tampilkan notice error di admin hanya untuk user yang berhak mengelola plugin.
 */
$my_custom_app_notice = static function ( string $message ): void {
	add_action(
		'admin_notices',
		static function () use ( $message ): void {
			if ( ! current_user_can( 'activate_plugins' ) ) {
				return;
			}
			printf( '<div class="notice notice-error"><p>%s</p></div>', esc_html( $message ) );
		}
	);
};

if ( PHP_VERSION_ID < 80100 ) {
	$my_custom_app_notice( 'My Custom App membutuhkan PHP 8.1 atau lebih baru.' );
	return;
}

$my_custom_app_autoload = __DIR__ . '/vendor/autoload.php';

if ( ! is_readable( $my_custom_app_autoload ) ) {
	$my_custom_app_notice( 'My Custom App: dependensi belum terpasang. Jalankan "composer install" di folder plugin.' );
	return;
}

require_once $my_custom_app_autoload;

unset( $my_custom_app_notice, $my_custom_app_autoload );

add_action(
	'plugins_loaded',
	static function (): void {
		Plugin::create( __FILE__ )->boot();
	}
);
