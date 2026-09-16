class TextFileReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.content = ""

    def read_file(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.content = f.read()

    def count_lines(self):
        return len(self.content.splitlines())

    def count_words(self):
        return len(self.content.split())

    def count_characters(self):
        return len(self.content)

    def display_content(self):
        print(self.content)


if __name__ == "__main__":
    reader = TextFileReader("test.txt")
    reader.read_file()
    reader.display_content()
    print("Lines:", reader.count_lines())
    print("Words:", reader.count_words())
    print("Characters:", reader.count_characters())
