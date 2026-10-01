<?php

declare(strict_types=1);

namespace MyCustomApp\Helpers;

/**
 * Kapabilitas kustom plugin. Diberikan ke peran DEFAULT_ROLES oleh Installer;
 * peran lain bisa ditambah dengan plugin manajemen peran tanpa mengubah kode.
 */
final class Capabilities
{
    /** Melihat, mengubah status, dan mengekspor booking survei. */
    public const MANAGE_BOOKINGS = 'mca_manage_bookings';

    public const DEFAULT_ROLES = ['administrator', 'editor'];

    private function __construct()
    {
    }
}
