<?php

declare(strict_types=1);

namespace MyCustomApp\Services;

use MyCustomApp\Helpers\Capabilities;
use MyCustomApp\Models\SchemaInterface;

/**
 * Membuat/memperbarui tabel kustom dan kapabilitas.
 *
 * Tidak memakai activation hook: maybe_upgrade() dicek di setiap request (satu
 * get_option yang ter-cache), sehingga juga berjalan saat plugin diperbarui
 * dengan menimpa file atau di multisite.
 */
final class Installer
{
    /** Naikkan setiap kali struktur tabel/kapabilitas berubah. */
    public const DB_VERSION = '1';
    public const OPTION     = 'my_custom_app_db_version';

    /** @var list<SchemaInterface> */
    private readonly array $tables;

    public function __construct(SchemaInterface ...$tables)
    {
        $this->tables = array_values($tables);
    }

    public function maybe_upgrade(): void
    {
        if (get_option(self::OPTION) === self::DB_VERSION) {
            return;
        }

        $this->install();
    }

    public function install(): void
    {
        require_once ABSPATH . 'wp-admin/includes/upgrade.php';

        foreach ($this->tables as $table) {
            dbDelta($table->schema_sql());
        }

        foreach (Capabilities::DEFAULT_ROLES as $role_name) {
            get_role($role_name)?->add_cap(Capabilities::MANAGE_BOOKINGS);
        }

        update_option(self::OPTION, self::DB_VERSION, false);
    }
}
