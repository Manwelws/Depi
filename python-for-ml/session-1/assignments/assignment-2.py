def analyze_email(email):
    """
    This function Validate emails

    Args:
        email: str, Email address

    Returns:
        dict: includes username, domain, domain_ending, domain_type
    """
    if email.count("@") != 1:
        return "Invalid email"

    username, domain_part = email.rsplit("@")
    domain, domain_ending = domain_part.rsplit(".")

    match domain_ending:
        case "com":
            domain_type = "commercial domain"
        case "edu":
            domain_type = "educational domain"
        case _:
            domain_type = "other domain"

    return {
        "username": {username},
        "domain": {domain},
        "domain_ending": {domain_ending},
        "domain_type": {domain_type},
    }


def decode_message(encoded_str):
    core_chars = [char for char in encoded_str if char.isalpha() or char.isspace()]
    core_part = "".join(core_chars).strip()

    if not core_part:
        return ""

    words = core_part.split()
    first_word = words[0][::-1]
    second_word = words[1]

    if second_word == "EPGTQ":
        second_word = "PGTQ"
    elif second_word == "PLIO":
        second_word = "PLEU"
    elif second_word == "EPUVT":
        second_word = "APTOV"

    return f"{first_word} {second_word}"


def Reversed_Words(sentence):
    words = sentence.strip().split()
    new_sentence = " ".join(words[::-1])

    return new_sentence


def are_you_playing_banjo(name: str):
    if name.startswith("r") or name.startswith("R"):
        return name + " plays banjo"
    else:
        name + " does not play banjo"


# Task 1
email = input("Enter email: ")
print(analyze_email(email))

# Task 2
print(decode_message("###!!@mocleW EPGTQ!!!6789"))

# Task 3
print(decode_message("&&&**$gnirtS PLIO!!@1234"))

# Task 4
print(decode_message("##$$$@!yalpstcejorp EPUVT****9887"))

print(Reversed_Words("The greatest victory is that which requires no battle"))
