def smart_join(strings, max_length=50):
    result = ""
    for i, string in enumerate(strings):
        # Add a newline if the string is long or the previous string was long
        if len(string) > max_length or (i > 0 and len(strings[i - 1]) > max_length):
            # Avoid adding a newline if the previous character is already a newline
            if not result.endswith("\n"):
                result += "\n"
        # Otherwise, add a space if the previous character is not a newline and it's not the first string
        elif i > 0 and not result.endswith("\n"):
            result += ",  "
        result += string
    if result.strip():
        return f"{result.strip()}, "
    return ""
