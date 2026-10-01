<?php

declare(strict_types=1);

namespace MyCustomApp\Models;

/**
 * Model yang memiliki tabel kustom. Dipakai Installer untuk dbDelta().
 */
interface SchemaInterface
{
    /**
     * Pernyataan CREATE TABLE lengkap dalam format yang diterima dbDelta()
     * (dua spasi setelah PRIMARY KEY, satu kolom per baris).
     */
    public function schema_sql(): string;
}
