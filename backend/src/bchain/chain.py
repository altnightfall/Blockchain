from .block import Block


class Chain:
    def __init__(self, start_block: Block):
        if not start_block.validate():
            raise ValueError("Cannot validate start block")
        self.blocks = [start_block]

    def __len__(self):
        return len(self.blocks)

    def __gt__(self, other):
        return len(self) > len(other)

    def __lt__(self, other):
        return len(self) < len(other)

    def validate(self) -> bool:
        for i in range(1, len(self.blocks)):
            temp_res = self.blocks[i].validate()
            if not temp_res:
                return False
            if self.blocks[i - 1].data["id"] + 1 != self.blocks[i].data["id"]:
                return False
            if self.blocks[i - 1].hash != self.blocks[i].hash:
                return False
        return True

    def find_block_by_id(self, id: int) -> Block | None:
        for block in self.blocks:
            if block.data["id"] == id:
                return block
        return None

    def find_block_by_hash(self, hash_inp: str) -> Block | None:
        for block in self.blocks:
            if block.hash == hash_inp:
                return block
        return None

    def most_recent_block(self):
        return self.blocks[-1]

    def max_index(self):
        return self.blocks[-1].data["id"]

    def add_block(self, block: Block) -> bool:
        if block.data["id"] > len(self):
            return False
        self.blocks.append(block)
        return True

    def block_list_dict(self):
        return [block.to_dict() for block in self.blocks]
