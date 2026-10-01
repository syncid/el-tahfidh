<?php
/**
 * Smoke test tanpa WordPress: php tests/smoke-test.php
 *
 * Fungsi/kelas WordPress yang dipakai diganti stub minimal. Repository memakai
 * implementasi palsu di memori, jam dipaku ke Jumat, 2 Okt 2026 10:30 WIB.
 * Folder tests/ tidak perlu ikut diunggah ke server.
 */

declare(strict_types=1);

namespace {
    require __DIR__ . '/../vendor/autoload.php';

    // ---- Stub WordPress ----------------------------------------------------
    $GLOBALS['__transients'] = [];
    $GLOBALS['__actions']    = [];

    function wp_unslash($v) { return is_string($v) ? stripslashes($v) : $v; }
    function sanitize_text_field(string $s): string {
        $s = strip_tags($s);
        $s = (string) preg_replace('/[\r\n\t ]+/', ' ', $s);
        return trim($s);
    }
    function sanitize_key(string $s): string { return (string) preg_replace('/[^a-z0-9_\-]/', '', strtolower($s)); }
    function get_transient(string $k) { return $GLOBALS['__transients'][$k] ?? false; }
    function set_transient(string $k, $v, int $ttl): bool { $GLOBALS['__transients'][$k] = $v; return true; }
    function add_action(string $hook, $cb, int $prio = 10): void { $GLOBALS['__actions'][] = $hook; }
    function apply_filters(string $hook, $value) { return $value; }
    function untrailingslashit(string $s): string { return rtrim($s, '/\\'); }
    function wp_parse_url(string $u) { return parse_url($u); }
    function home_url(): string { return 'https://eltahfidh.or.id'; }
    function __(string $s, string $d = ''): string { return $s; }

    class WP_REST_Server { public const CREATABLE = 'POST'; public const READABLE = 'GET'; }
    class WP_Error {
        public function __construct(public string $code = '', public string $message = '', public $data = null) {}
    }
    class WP_REST_Response {
        public array $headers = [];
        public function __construct(public $data = null, public int $status = 200) {}
        public function header(string $k, string $v): void { $this->headers[$k] = $v; }
    }
    class WP_REST_Request {
        public function __construct(private string $body, private array $headers = []) {}
        public function get_body(): string { return $this->body; }
        public function get_header(string $k): ?string { return $this->headers[strtolower($k)] ?? null; }
    }
}

namespace MyCustomApp\Tests {

    use DateTimeImmutable;
    use DateTimeZone;
    use MyCustomApp\Controllers\Admin\SurveyBookingAdminController;
    use MyCustomApp\Controllers\SurveyBookingController;
    use MyCustomApp\Models\SurveyBookingRepositoryInterface;
    use MyCustomApp\Plugin;
    use MyCustomApp\Providers\HookableInterface;
    use MyCustomApp\Services\ClockInterface;
    use MyCustomApp\Services\RateLimiter;
    use MyCustomApp\Services\SurveyBookingService;
    use MyCustomApp\Services\SurveyBookingValidator;
    use MyCustomApp\Services\ValidationException;
    use WP_Error;
    use WP_REST_Request;

    final class FixedClock implements ClockInterface
    {
        public function now(): DateTimeImmutable
        {
            return new DateTimeImmutable('2026-10-02 10:30:00', new DateTimeZone('Asia/Jakarta'));
        }
    }

    final class MemoryRepo implements SurveyBookingRepositoryInterface
    {
        /** @var array<int, array<string, mixed>> */
        public array $rows = [];

        public function find_active_duplicate(string $wa, string $santri, string $tanggal): ?array
        {
            foreach ($this->rows as $r) {
                if ($r['wa'] === $wa && strcasecmp($r['santri'], $santri) === 0 && $r['tanggal'] === $tanggal && $r['status'] !== self::STATUS_BATAL) {
                    return $r;
                }
            }
            return null;
        }

        public function insert(array $data): int
        {
            $id              = count($this->rows) + 1;
            $this->rows[$id] = ['id' => $id] + $data;
            return $id;
        }

        public function update(int $id, array $data): bool
        {
            $this->rows[$id] = $data + $this->rows[$id];
            return true;
        }
    }

    $pass = 0;
    $fail = 0;
    $check = static function (string $name, bool $ok) use (&$pass, &$fail): void {
        $ok ? $pass++ : $fail++;
        echo ($ok ? '  [OK]    ' : '  [GAGAL] ') . $name . PHP_EOL;
    };
    $throws = static function (callable $fn, ?int $status = null, ?string $field = null): bool {
        try {
            $fn();
        } catch (ValidationException $e) {
            return ($status === null || $e->http_status() === $status)
                && ($field === null || array_key_exists($field, $e->errors()));
        }
        return false;
    };

    $clock = new FixedClock();
    $valid = [
        'jenjang' => 'smp', 'ortu' => '  ahmad   fauzi ', 'wa' => '0812-3456-7890', 'santri' => 'muhammad al-fatih',
        'kelas' => 'SD Kelas 6', 'domisili' => 'Cileungsi', 'tanggal' => '2026-10-05', 'sesi' => '08.00', 'website' => '',
    ];

    echo "Validator\n";
    $v = new SurveyBookingValidator($clock);
    $d = $v->validate($valid);
    $check('jenjang dinormalisasi ke huruf besar', $d['jenjang'] === 'SMP');
    $check('nama orang tua dikapitalisasi & spasi dirapikan', $d['ortu'] === 'Ahmad Fauzi');
    $check('nama santri dikapitalisasi setelah tanda hubung', $d['santri'] === 'Muhammad Al-Fatih');
    $check('WA 0812-3456-7890 -> 6281234567890', $d['wa'] === '6281234567890');
    $check('WA 8123... -> 628123...', SurveyBookingValidator::normalize_wa('81234567890') === '6281234567890');
    $check('WA tidak valid ditolak', $throws(fn () => $v->validate(['wa' => '12345'] + $valid), 422, 'wa'));
    $check('jenjang selain SMP/SMA ditolak', $throws(fn () => $v->validate(['jenjang' => 'SD'] + $valid), 422, 'jenjang'));
    $check('kelas di luar daftar ditolak', $throws(fn () => $v->validate(['kelas' => 'Kuliah'] + $valid), 422, 'kelas'));
    $check('tag HTML dibuang dari nama', $v->validate(['ortu' => '<b>Siti</b> aminah'] + $valid)['ortu'] === 'Siti Aminah');
    $check('tanggal kemarin ditolak', $throws(fn () => $v->validate(['tanggal' => '2026-10-01'] + $valid), 422, 'tanggal'));
    $check('tanggal tidak valid (31 Feb) ditolak', $throws(fn () => $v->validate(['tanggal' => '2027-02-31'] + $valid), 422, 'tanggal'));
    $check('hari ke-60 diterima', $v->validate(['tanggal' => '2026-12-01'] + $valid)['tanggal'] === '2026-12-01');
    $check('hari ke-61 ditolak', $throws(fn () => $v->validate(['tanggal' => '2026-12-02'] + $valid), 422, 'tanggal'));
    $check('hari ini sesi 08.00 (sudah lewat jam 10.30) ditolak', $throws(fn () => $v->validate(['tanggal' => '2026-10-02'] + $valid), 422, 'sesi'));
    $check('hari ini sesi 11.00 diterima', $v->validate(['tanggal' => '2026-10-02', 'sesi' => '11.00'] + $valid)['sesi'] === '11.00');
    $check('sesi di luar daftar ditolak', $throws(fn () => $v->validate(['sesi' => '09.00'] + $valid), 422, 'sesi'));
    $check('nilai array (bukan teks) ditolak', $throws(fn () => $v->validate(['santri' => ['x']] + $valid), 422, 'santri'));

    echo "\nService\n";
    $repo    = new MemoryRepo();
    $service = new SurveyBookingService($repo, $v, new RateLimiter(), $clock);
    $r1      = $service->book($valid, '10.0.0.1');
    $check('booking baru dapat kode SMP-26001', $r1->kode === 'SMP-26001' && $r1->dobel === false);
    $check('baris tersimpan dengan status terjadwal & created_at UTC', $repo->rows[1]['status'] === 'terjadwal' && $repo->rows[1]['created_at'] === '2026-10-02 03:30:00');
    $r2 = $service->book(['sesi' => '15.00', 'santri' => 'MUHAMMAD AL-FATIH'] + $valid, '10.0.0.1');
    $check('anak & tanggal sama -> tiket lama (dobel, sesi lama)', $r2->dobel && $r2->kode === 'SMP-26001' && $r2->sesi === '08.00' && count($repo->rows) === 1);
    $repo->rows[1]['status'] = 'batal';
    $r3 = $service->book($valid, '10.0.0.1');
    $check('setelah dibatalkan boleh booking ulang', ! $r3->dobel && $r3->kode === 'SMP-26002');
    $check('honeypot terisi ditolak (400) tanpa menyimpan', $throws(fn () => $service->book(['website' => 'http://spam'] + $valid, '10.0.0.2'), 400) && count($repo->rows) === 2);

    $GLOBALS['__transients'] = [];
    for ($i = 0; $i < SurveyBookingService::RATE_LIMIT; $i++) {
        try { $service->book(['tanggal' => '2026-10-0' . (6 + $i % 3)] + $valid, '10.0.0.9'); } catch (ValidationException) {}
    }
    $check('percobaan ke-11 dari IP sama ditolak (429)', $throws(fn () => $service->book($valid, '10.0.0.9'), 429));
    $check('IP lain tidak ikut terblokir', ! $service->book(['santri' => 'Zahra'] + $valid, '10.0.0.10')->dobel);

    echo "\nController REST (kontrak form GitHub)\n";
    $GLOBALS['__transients'] = [];
    $controller = new SurveyBookingController(new SurveyBookingService(new MemoryRepo(), $v, new RateLimiter(), $clock), ['https://eltahfidh.github.io']);
    $req = static fn (array $payload): WP_REST_Request => new WP_REST_Request((string) json_encode($payload), ['origin' => 'https://eltahfidh.github.io']);

    $res = $controller->store($req(['action' => 'booking', 'data' => $valid]));
    $check('sukses: HTTP 201 {"ok":true,"kode":"SMP-26001"}', $res->status === 201 && $res->data === ['ok' => true, 'kode' => 'SMP-26001']);
    $check('respons tidak di-cache (Cache-Control: no-store)', ($res->headers['Cache-Control'] ?? '') === 'no-store');
    $res = $controller->store($req(['action' => 'booking', 'data' => $valid]));
    $check('dobel: {"ok":true,"kode":...,"dobel":true,"sesi":"08.00"}', $res->status === 200 && $res->data === ['ok' => true, 'kode' => 'SMP-26001', 'dobel' => true, 'sesi' => '08.00']);
    $res = $controller->store($req(['action' => 'booking', 'data' => ['wa' => 'x'] + $valid]));
    $check('invalid: HTTP 422 {"ok":false,"error":"Nomor WhatsApp..."}', $res->status === 422 && $res->data['ok'] === false && str_starts_with($res->data['error'], 'Nomor WhatsApp'));
    $res = $controller->store(new WP_REST_Request('bukan json', []));
    $check('body bukan JSON: HTTP 400 ok=false', $res->status === 400 && $res->data['ok'] === false);
    $res = $controller->store($req(['action' => 'hapus', 'data' => $valid]));
    $check('action selain "booking" ditolak 400', $res->status === 400);
    $res = $controller->store(new WP_REST_Request(str_repeat('x', 9000), []));
    $check('body > 8 KB ditolak 413', $res->status === 413);

    $check('origin eltahfidh.github.io diizinkan', $controller->check_origin($req([])) === true);
    $check('origin situs sendiri diizinkan', $controller->check_origin(new WP_REST_Request('', ['origin' => 'https://eltahfidh.or.id'])) === true);
    $check('origin asing ditolak 403', ($e = $controller->check_origin(new WP_REST_Request('', ['origin' => 'https://evil.example']))) instanceof WP_Error && $e->data['status'] === 403);
    $check('tanpa header Origin ditolak', $controller->check_origin(new WP_REST_Request('', [])) instanceof WP_Error);

    echo "\nLain-lain\n";
    $check('CSV injection: "=HYPERLINK(...)" diberi awalan \'', SurveyBookingAdminController::csv_cell('=HYPERLINK("x")') === "'=HYPERLINK(\"x\")");
    $check('CSV: teks biasa tidak diubah', SurveyBookingAdminController::csv_cell('Ahmad') === 'Ahmad');

    $counter  = new class implements HookableInterface {
        public int $calls = 0;
        public function register_hooks(): void { $this->calls++; }
    };
    $plugin = new Plugin(__FILE__, $counter);
    $plugin->boot();
    $plugin->boot();
    $check('Plugin::boot() memanggil register_hooks() tepat sekali', $counter->calls === 1);

    echo PHP_EOL . sprintf('Hasil: %d lulus, %d gagal', $pass, $fail) . PHP_EOL;
    exit($fail === 0 ? 0 : 1);
}
