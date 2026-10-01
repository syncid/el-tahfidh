<?php

declare(strict_types=1);

namespace MyCustomApp\Helpers;

use InvalidArgumentException;

/**
 * Sanitasi input form berbasis whitelist skema.
 *
 * Contoh:
 *   $data = Sanitizer::by_schema($_POST, ['nama' => 'text', 'email' => 'email', 'umur' => 'int']);
 *
 * Field di luar skema dibuang. Input superglobal ($_POST/$_GET) di-wp_unslash() otomatis;
 * untuk data REST/JSON (tidak pernah di-slash) kirim $unslash = false.
 * Sanitasi bukan validasi: cek wajib-isi/format tetap dilakukan di Service.
 */
final class Sanitizer
{
    public const TYPES = ['text', 'textarea', 'email', 'int', 'float', 'bool', 'url', 'key'];

    private function __construct()
    {
    }

    /**
     * @param array<string, mixed>  $input  Data mentah, mis. $_POST.
     * @param array<string, string> $schema  field => tipe (lihat TYPES).
     * @param bool                  $unslash true untuk superglobal, false untuk JSON.
     * @return array<string, mixed>
     */
    public static function by_schema(array $input, array $schema, bool $unslash = true): array
    {
        $clean = [];

        foreach ($schema as $field => $type) {
            $raw           = $input[$field] ?? null;
            $clean[$field] = self::value($unslash && is_string($raw) ? wp_unslash($raw) : $raw, $type);
        }

        return $clean;
    }

    /**
     * Sanitasi satu nilai skalar. Array/objek ditolak (menjadi null).
     */
    public static function value(mixed $value, string $type): mixed
    {
        if (! in_array($type, self::TYPES, true)) {
            throw new InvalidArgumentException(sprintf('Tipe sanitasi tidak dikenal: %s', $type));
        }

        if ($value !== null && ! is_scalar($value)) {
            return null;
        }

        $value = (string) ($value ?? '');

        return match ($type) {
            'text'     => sanitize_text_field($value),
            'textarea' => sanitize_textarea_field($value),
            'email'    => sanitize_email($value),
            'int'      => filter_var($value, FILTER_VALIDATE_INT, FILTER_NULL_ON_FAILURE),
            'float'    => filter_var($value, FILTER_VALIDATE_FLOAT, FILTER_NULL_ON_FAILURE),
            'bool'     => filter_var($value, FILTER_VALIDATE_BOOLEAN),
            'url'      => esc_url_raw($value),
            'key'      => sanitize_key($value),
        };
    }
}
