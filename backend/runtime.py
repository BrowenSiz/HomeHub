class VaultRuntime:
    def __init__(self):
        self.master_key: bytes | None = None

    def set_key(self, key: bytes):
        self.master_key = key

    def get_key(self) -> bytes | None:
        return self.master_key

    def clear(self):
        self.master_key = None

vault_state = VaultRuntime()