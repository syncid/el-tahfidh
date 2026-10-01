<?php

declare(strict_types=1);

namespace MyCustomApp\Services;

use RuntimeException;

/**
 * Input pengguna ditolak. Pesannya AMAN ditampilkan ke pengguna
 * (berbeda dengan exception lain yang hanya boleh masuk log).
 */
final class ValidationException extends RuntimeException
{
    /**
     * @param array<string, string> $errors field => pesan.
     */
    public function __construct(
        string $message,
        private readonly array $errors = [],
        private readonly int $http_status = 422
    ) {
        parent::__construct($message);
    }

    /**
     * @return array<string, string>
     */
    public function errors(): array
    {
        return $this->errors;
    }

    public function http_status(): int
    {
        return $this->http_status;
    }
}
