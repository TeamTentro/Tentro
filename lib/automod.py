
"""
Utilities to provide a powerful blacklist
"""

from typing import Dict, List, Pattern, Set, Tuple, Union
import re
import math
import unicodedata

PUNCTUATION: List[str] = [".", ",", "'",
                          ";", '"', "`", ":", "!", "?", "-", "_"]


__CHECK_BL_DIRECT: int = 0


def check_bl_direct() -> int:
    """
    "Checks for blacklisted words directly.\n
    Blacklisted word: hello
    'hello guys' is BL\n
    'helloguys' isn't BL\n
    """
    return __CHECK_BL_DIRECT


__CHECK_BL_FILLERS: int = 1


def check_bl_fillers() -> int:
    """
    Checks for blacklisted with 'filler' characters in them\n
    Blacklisted word: hello\n
    Fillers: [" ", "-"]\n
    'h e l l o guys' is BL\n
    'h e l l oguys' is BL\n
    'h e-l l-o guys' is BL\n
    'h e   l   l o guys' is BL
    """
    return __CHECK_BL_FILLERS


__CHECK_BL_AGGRESSIVE: int = 2


def check_bl_aggressive() -> int:
    """
    Checks for blacklisted very aggressively\n
    Don't completely rely on this as it can generate a lot of false positives\n

    Blacklisted word: hello\n
    Threshold: 3\n
    HxxxExxxLxxxLxxxO is BL\n
    HxsfEsdlLsrtLsO is BL\n
    HxxxxELLO isn't BL\n
    """
    return __CHECK_BL_AGGRESSIVE


__CHECK_SPAM_BY_REPETITION: int = 3


def check_spam_by_repetition() -> int:
    """
    Checks for spam by repetition
    """
    return __CHECK_SPAM_BY_REPETITION


__CHECK_SPAM_ALTERNATING_CASES: int = 4


def check_spam_alternating_cases() -> int:
    """
    Checks for tHiS tYpIng StYle
    """
    return __CHECK_SPAM_ALTERNATING_CASES


__CHECK_SPAM_LETTERS: int = 5

__SPAM_LETTERS_THRESHOLD: int = 4


def check_spam_repeating_letters() -> int:
    """
    Checks for repeating letters such as in 'eeeeeeeeeee'
    """
    return __CHECK_SPAM_LETTERS


__CHECK_SPAM_CAPS: int = 6

__CAP_SPAM_THRESHOLD: int = 8


def check_spam_caps() -> int:
    return __CHECK_SPAM_CAPS


def generate_replacements(words: List[str], replacement_dict: Dict[str, List[str]]) -> List[str]:
    """
    Expand the blacklist by replacing certain letters
    or letter combinations with potentially same meanings\n
    words: ["late", "mate", "aterate"]\n
    replacement_dict: {"ate": [8]};\n
    Returns ["late", "mate", "aterate", "l8", "m8", "8rate", "ater8"]\n
    This is an expensive operation, avoid calling it multiple times
    """
    replacements: List[str] = []
    for word in words:
        replacements += __get_all_replacements(word, replacement_dict)
    return replacements


def create_single_censor(words: List[str]) -> List[str]:
    """
    Creates possibly censored versions of words
    Word: "Hello"
    Output: ["*ello", "h*llo", "he*lo", "hel*o", "hell*"]
    """
    censored: List[str] = []
    for word in words:
        for character in range(len(word)):
            copy_word = list(word)
            copy_word[character] = r"*"
            censored.append("".join(copy_word))
    return censored

def message_to_ascii(message: str) -> str:
    """
    Converts unicode characters to their ASCII equivalents
    Letters with like à become a
    """
    text = unicodedata.normalize('NFD', message)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)


def __get_all_replacements(word: str, replacement_dict: Dict[str, List[str]]) -> List[str]:
    generated: List[str] = []
    for key in replacement_dict.keys():
        index = word.find(key)
        # Find will return -1 if nothing is found
        if index != -1:
            replacements: List[str] = replacement_dict[key]
            for replacement in replacements:
                # Replace the first one only
                replaced: str = word.replace(key, replacement, 1)
                sub_replacements = __get_all_replacements(
                    replaced[index:], replacement_dict)
                generated.append(replaced)
                if sub_replacements is not None:
                    for sub_replacement in sub_replacements:
                        generated.append(replaced[:index] + sub_replacement)
    return generated


def __tokenize(message: str) -> List[str]:
    tokens: List[str] = message.split(" ")

    # string.replace produces a copy of the original string,
    #  it doesn't mutate it thus we have to use indices
    for index, token in enumerate(tokens):
        for punctuation in PUNCTUATION:
            tokens[index] = token.replace(punctuation, "")
    return tokens


def __update_spam_probability(old_probability: float, predicted: float) -> float:
    return max(old_probability,
               math.sqrt((old_probability * old_probability + predicted * predicted) * 0.5))


def get_spam_probability(message: str, spam_algorithms: List[int]) -> float:
    """
    Check the given message for spam using a list of spam algorithms\n
    All the spam algorithm names start by check_spam\n
    This method will return the probability of the message being spam
    """

    factor = math.tanh(len(message) / 10)

    spam_probability: float = 0
    for algo in spam_algorithms:
        if algo == check_spam_by_repetition():
            spam_probability = __update_spam_probability(
                spam_probability, __check_repetition(message))
        elif algo == check_spam_alternating_cases():
            spam_probability = __update_spam_probability(
                spam_probability, __check_alternating_cases(message))
        elif algo == check_spam_repeating_letters():
            spam_probability = __update_spam_probability(
                spam_probability, __check_repeating_letters(message))
        elif algo == check_spam_caps():
            spam_probability = __update_spam_probability(
                spam_probability, __check_caps(message))

    return spam_probability * factor


def __check_repetition(message: str) -> float:
    lowercase_message: str = message.lower()
    tokens: List[str] = __tokenize(message)
    message_len: int = sum([len(token) for token in tokens])
    spam_probability: float = 0
    for token in tokens:
        count: int = (lowercase_message.count(
            token.lower()) - 1) * len(token)
        ratio: float = count / message_len
        spam_probability = __update_spam_probability(
            spam_probability, ratio)
    return spam_probability


def __check_alternating_cases(message: str) -> float:
    tokens: List[str] = __tokenize(message)
    joined: str = "".join(tokens)
    message_len = len(joined)
    previous: str = joined[0]
    alternating_count: int = 0
    for character in joined:
        if character.isupper() is not previous.isupper():
            alternating_count += 1
        previous = character
    return alternating_count / message_len


def __check_repeating_letters(message: str) -> float:
    tokens: List[str] = __tokenize(message)
    joined: str = "".join(tokens)
    message_len = len(joined)
    previous: str = joined[0]

    repeating_count = 0
    for character in joined:
        if character is previous:
            repeating_count += 1
        previous = character
    if repeating_count > __SPAM_LETTERS_THRESHOLD:
        return (repeating_count - __SPAM_LETTERS_THRESHOLD) / message_len
    return 0


def __check_caps(message: str) -> float:
    tokens: List[str] = __tokenize(message)
    joined: str = "".join(tokens)
    message_len = len(joined)
    caps_count = 0
    for character in joined:
        if character.isupper():
            caps_count += 1
    if caps_count > __CAP_SPAM_THRESHOLD:
        return caps_count / message_len
    return 0


def check_bl(message: str, bl_words: List[str], bl_algorithms: List[int],
             fillers: List[str] = None, check_threshold: int = None) -> Union[None, Set[str]]:
    """
    Checks for blacklisted words with the given algorithms\n
    All the algorithm names start by 'check_bl'\n
    All BL words must be lower case\n
    Returns None if there are no blacklisted words or returns a list of blacklisted words
    """
    check_message: str = message.lower()
    tokens: List[str] = __tokenize(check_message)

    found_words: List[str] = []
    for algorithm in bl_algorithms:
        if algorithm == check_bl_direct():
            found_words += __check_direct(tokens, bl_words)
        elif algorithm == check_bl_fillers():
            found_words += __check_fillers(check_message, bl_words, fillers)
        elif algorithm == check_bl_aggressive():
            found_words += __check_aggressive(check_message,
                                              bl_words, check_threshold)
    return set(found_words)


def __check_direct(tokens: List[str], bl_words: List[str]) -> List[str]:
    found_words = []
    if tokens is not None:
        for word in bl_words:
            if word in tokens:
                found_words.append(word)
    return found_words


def __check_fillers(message: str, bl_words: List[str], fillers: List[str]) -> List[str]:
    found_words: List[str] = []
    if fillers is None:
        print("Fillers BL mechanism has been called however no fillers have been provided")
    else:
        for bl_word in bl_words:
            regex: str = ""
            for character in bl_word:
                regex += f"[{character}]"
                if len(fillers) > 0:
                    regex += "["
                    regex += fillers[0]
                    for filler_index in range(1, len(fillers)):
                        regex += f"|{fillers[filler_index]}"
                    regex += "]*"
            pattern: Pattern = re.compile(regex)
            if re.search(pattern, message) is not None:
                found_words.append(bl_word)
    return found_words


def __check_aggressive(message: str, bl_words: List[str], check_threshold: int) -> List[str]:

    found_words: List[str] = []
    if check_threshold is None:
        print("Aggressive BL has been called however no letter threshold has been provided")
    else:
        regexes: List[Tuple[str, Pattern]] = []
        if bl_words is not None:
            for bl_word in bl_words:
                regex = __generate_aggressive_filter(
                    bl_word, check_threshold)
                regexes.append((bl_word, regex))

        for (word, regex) in regexes:
            if re.search(regex, message) is not None:
                found_words.append(word)
    return found_words


def __generate_aggressive_filter(word: str, threshold: int) -> Pattern:
    regex = ""
    for character in range(len(word) - 1):
        regex += f"[{word[character]}]"
        regex += "(.*?){0," + str(threshold) + "}"
    regex += f"[{word[-1]}]"
    return re.compile(regex)


def __test():
    fillers = [r"\s", "-"]
    messages = ["I will Aksy you codeize!",
                "Arggh bl, I will a-k-s-y you c O  d E i  Z      e!",
                "Dang, this BL is OP, respects from A k   - s Y",
                "Haha imma A word bait a||ksy||",
                "Akxxxsy"]
    bl_words = ["aksy", "codeize"]
    bl_algorithms = [check_bl_direct(), check_bl_fillers(),
                     check_bl_aggressive()]

    print(f"bl words: {bl_words}")
    for message in messages:
        print(f"message is: {message}")
        print(f"detected bl words: \
            {check_bl(message, bl_words, bl_algorithms, fillers=fillers, check_threshold=3)}")

    bl_words = generate_replacements(["your mom"], {"you": ["u"]})
    message = "ur mom"
    print(check_bl(message, bl_words, bl_algorithms,
          fillers=fillers, check_threshold=3))

    messages = ["RaId ShAdOw LeGeNdS iS a GrEaT gAmE",
                "UwU UwU",
                "EEEEEEEEEEEEEE"]
    for message in messages:
        print(f"message: {message}")
        spam_probability = get_spam_probability(message,
                                                spam_algorithms=[check_spam_by_repetition(),
                                                                 check_spam_alternating_cases(),
                                                                 check_spam_repeating_letters(),
                                                                 check_spam_caps()])
        print(
            f"spam probabilty: {spam_probability}")








from typing import Dict, List, Tuple, Union


__MINUTES = 60
__HOURS = __MINUTES * 60
__DAYS = __HOURS * 24


_TYPES: List[Tuple[str, str]] = [
    ("seconds", "s"), ("minutes", "m"), ("hours", "h"), ("days", "d")]
_RATIOS: List[Tuple[str, int]] = [
    ("seconds", 1), ("minutes", __MINUTES), ("hours", __HOURS), ("days", __DAYS)]


def _parse_unit(arg: str, unit: str) -> Union[None, int]:
    if arg.endswith(unit):
        duration = arg[:-len(unit)]
        if duration.isnumeric():
            return duration
    return None


class Command:
    __arguments: Dict[str, Union[str, int]]

    def __init__(self, args: str):
        arg_list: List[str] = args.split()
        arguments: Dict[str, Union[str, int]] = {}

        for index, arg in enumerate(arg_list):
            found_arg = False
            for (name, unit) in _TYPES:
                value = _parse_unit(arg, unit)
                if value is not None:
                    found_arg = True
                    arguments[name] = int(value)
                    break
            if not found_arg:
                arguments["content"] = " ".join(arg_list[index:])
                break
        self.__arguments = arguments

    def get_value_of(self, name: str) -> Union[None, str, int]:
        if name in self.__arguments:
            return self.__arguments[name]
        return None

    def get_content(self) -> Union[None, str]:
        if "content" in self.__arguments:
            return self.__arguments["content"]
        return None


def get_time(command: Command) -> Union[None, int]:
    seconds: int = 0
    time_given: bool = False
    for (name, ratio) in _RATIOS:
        time: Union[str, int] = command.get_value_of(name)
        if time is not None and isinstance(time, int):
            time_given = True
            seconds += time * ratio
    if time_given:
        return seconds
    return None


def __test():
    command_str = " love u tony"
    command = Command(command_str)
    print(f"command: {command_str}")
    print(f"time in seconds: {get_time(command)}")
    print(f"content: {command.get_content()}")


if __name__ == "__main__":
    __test()
