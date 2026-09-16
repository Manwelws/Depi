def read_txt_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return f"Error: The file '{file_path}' was not found."
    except IOError:
        return "Error: An error occurred while reading the file."


class UserExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.usernames = {}

    def extract_usernames(self):
        content = read_txt_file(self.file_path)

        if content.startswith("Error"):
            return content

        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            username, sep, password = line.partition(':')
            if sep:
                self.usernames[username] = password

        return self.usernames


if __name__ == "__main__":
    extractor = UserExtractor("test.txt")
    result = extractor.extract_usernames()
    print(result)
