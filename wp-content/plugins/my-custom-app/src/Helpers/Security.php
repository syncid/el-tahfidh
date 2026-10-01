<?php

declare(strict_types=1);

namespace MyCustomApp\Helpers;

/**
 * Penjaga keamanan untuk form submission (admin-post.php) dan AJAX (admin-ajax.php).
 * Untuk REST API gunakan AbstractRestController::require_capability().
 *
 * Urutan wajib di setiap handler POST: verify_nonce_or_die() lalu require_capability_or_die(),
 * baru kemudian sanitasi input dan panggil Service.
 */
final class Security
{
    private function __construct()
    {
    }

    /**
     * Hentikan request (HTTP 403) jika nonce POST tidak valid atau kedaluwarsa.
     * Pasangkan dengan wp_nonce_field($action, $field) di form.
     */
    public static function verify_nonce_or_die(string $action, string $field = '_wpnonce'): void
    {
        // phpcs:ignore WordPress.Security.NonceVerification.Missing -- ini justru tempat verifikasinya.
        $raw   = $_POST[$field] ?? '';
        $nonce = is_string($raw) ? sanitize_text_field(wp_unslash($raw)) : '';

        if (! wp_verify_nonce($nonce, $action)) {
            wp_die(
                esc_html__('Sesi tidak valid atau kedaluwarsa. Muat ulang halaman lalu coba lagi.', 'my-custom-app'),
                esc_html__('Permintaan ditolak', 'my-custom-app'),
                ['response' => 403]
            );
        }
    }

    /**
     * Hentikan request (HTTP 403) jika user tidak memiliki kapabilitas.
     */
    public static function require_capability_or_die(string $capability): void
    {
        if (! current_user_can($capability)) {
            wp_die(
                esc_html__('Anda tidak memiliki izin untuk aksi ini.', 'my-custom-app'),
                esc_html__('Akses ditolak', 'my-custom-app'),
                ['response' => 403]
            );
        }
    }
}
