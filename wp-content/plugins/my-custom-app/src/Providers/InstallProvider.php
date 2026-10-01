<?php

declare(strict_types=1);

namespace MyCustomApp\Providers;

use MyCustomApp\Services\Installer;

/**
 * Pastikan tabel & kapabilitas mutakhir sebelum fitur lain berjalan.
 */
final class InstallProvider implements HookableInterface
{
    public function __construct(private readonly Installer $installer)
    {
    }

    public function register_hooks(): void
    {
        add_action('init', [$this->installer, 'maybe_upgrade'], 5);
    }
}
