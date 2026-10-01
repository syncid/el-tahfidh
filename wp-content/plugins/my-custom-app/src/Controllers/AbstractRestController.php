<?php

declare(strict_types=1);

namespace MyCustomApp\Controllers;

use MyCustomApp\Helpers\ResponseFormatter;
use Throwable;
use WP_Error;
use WP_REST_Response;

/**
 * Basis semua controller REST.
 *
 * Aturan:
 * - Controller hanya menerima request lalu memanggil Service/Model. Tidak ada query di sini.
 * - Setiap route WAJIB punya permission_callback (lihat route()); tidak ada default publik.
 * - CSRF: untuk login berbasis cookie, WordPress Core memverifikasi header X-WP-Nonce
 *   (aksi 'wp_rest') sebelum route dijalankan. Tanpa nonce valid, user dianggap belum login,
 *   sehingga require_capability() otomatis menolak. Jangan menambah wp_verify_nonce() manual
 *   di REST karena akan merusak autentikasi Application Password.
 */
abstract class AbstractRestController implements RestControllerInterface
{
    public const API_NAMESPACE = 'my-custom-app/v1';

    /**
     * @param string|list<string>                $methods    Gunakan konstanta WP_REST_Server.
     * @param callable                           $permission Hasil require_capability() atau callback sejenis.
     * @param array<string, array<string, mixed>> $args       Skema argumen: type, required,
     *                                                        sanitize_callback, validate_callback.
     */
    protected function route(
        string $route,
        string|array $methods,
        callable $callback,
        callable $permission,
        array $args = []
    ): void {
        register_rest_route(
            self::API_NAMESPACE,
            $route,
            [
                'methods'             => $methods,
                'callback'            => $callback,
                'permission_callback' => $permission,
                'args'                => $args,
            ]
        );
    }

    /**
     * Permission callback: user harus terautentikasi dan memiliki kapabilitas tertentu.
     * Mengembalikan 401 untuk tamu dan 403 untuk user yang login tapi tidak berhak.
     */
    protected function require_capability(string $capability): callable
    {
        return static function () use ($capability): bool|WP_Error {
            if (current_user_can($capability)) {
                return true;
            }

            return ResponseFormatter::error(
                'mca_forbidden',
                __('Anda tidak memiliki izin untuk aksi ini.', 'my-custom-app'),
                rest_authorization_required_code()
            );
        };
    }

    /**
     * Jalankan aksi controller dengan penanganan error terpusat.
     * Detail exception hanya dicatat ke log, tidak pernah dikirim ke klien.
     *
     * @param callable(): (WP_REST_Response|WP_Error) $action
     */
    protected function handle(callable $action): WP_REST_Response|WP_Error
    {
        try {
            return $action();
        } catch (Throwable $e) {
            $this->log_exception($e);

            return ResponseFormatter::error(
                'mca_internal_error',
                __('Terjadi kesalahan pada server. Silakan coba lagi.', 'my-custom-app'),
                500
            );
        }
    }

    /**
     * Catat detail exception ke log server (bukan ke respons).
     */
    protected function log_exception(Throwable $e): void
    {
        error_log(
            sprintf('[my-custom-app] %s: %s in %s:%d', $e::class, $e->getMessage(), $e->getFile(), $e->getLine())
        );
    }
}
