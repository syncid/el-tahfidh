from dataclasses import dataclass


@dataclass(frozen=True)
class Site:
    """Satu instalasi WordPress yang diekspor.

    key      : nama folder di db/, mis. 'utama' atau 'smp-quran-putra'.
    host     : nama domain tanpa skema.
    jenjang  : halaman jenjang tujuan di situs baru ('smp', 'sma', 'ifs', 'psb'),
               None untuk situs induk.
    """

    key: str
    host: str
    label: str
    jenjang: str | None = None

    @property
    def api_base(self) -> str:
        return f"https://{self.host}/wp-json"

    @property
    def is_main(self) -> bool:
        return self.jenjang is None
