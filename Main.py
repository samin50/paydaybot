from src.Processor import Processor
from src.UI import UI

if __name__ == "__main__":
    processor = Processor(UI())
    processor.state_machine()
