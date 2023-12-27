def is_valid_syntax(s):
    stack = []
    opening_brackets = "({["
    closing_brackets = ")}]"

    for char in s:
        if char in opening_brackets:
            stack.append(char)
        elif char in closing_brackets:
            if not stack or opening_brackets[closing_brackets.index(char)] != stack.pop():
                return False

    return not stack


print(is_valid_syntax("()(()())"))  
print(is_valid_syntax("))))"))      
print(is_valid_syntax(")("))       
