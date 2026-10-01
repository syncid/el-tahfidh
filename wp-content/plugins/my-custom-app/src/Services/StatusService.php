<?php

declare(strict_types=1);

namespace MyCustomApp\Services;

/**
 * Menyusun informasi lingkungan plugin. Logika murni, tanpa akses request.
 */
final class StatusService
{
    public function __construct(private readonly string $plugin_file)
    {
    }

    /**
     * @return array{plugin_version: string, php_version: string, wp_version: string}
     */
    public function report(): array
    {
        $headers = get_file_data($this->plugin_file, ['version' => 'Version'], 'plugin');

        return [
            'plugin_version' => (string) $headers['version'],
            'php_version'    => PHP_VERSION,
            'wp_version'     => (string) get_bloginfo('version'),
        ];
    }
}
