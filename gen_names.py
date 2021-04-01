
def distribute_chars_into_stringlist(chars, str_list) :
    if chars:
        return set(distribute_char_into_stringlist(chars[0], distribute_chars_into_stringlist(chars[1:], str_list)))
    else:
        return str_list        

def distribute_char_into_stringlist(char, str_list):
    result = []
    for s in str_list:
        for i in range(len(s)+1):
            result.append(s[:i] + char + s[i:])
    return result

if __name__ == '__main__':

    print( distribute_chars_into_stringlist('x', ['abc']) )
    
    print( distribute_chars_into_stringlist('xy', ['abc']) )

    print( distribute_chars_into_stringlist('66', ['999']) )

    print( distribute_chars_into_stringlist('666', ['999']) )

