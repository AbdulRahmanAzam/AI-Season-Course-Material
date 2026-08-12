"""
THE CURRICULUM  (data only - this is not a lesson file)
=======================================================
Everything ARGPT-Coder will ever know is written down here, by hand.

That sentence sounds like a limitation. It is actually the whole point of
this session. A 25M parameter model cannot invent knowledge, so we choose
its knowledge deliberately and then we can honestly test whether it learned
it. Big labs do exactly this, just with millions of examples instead of 130.

Two kinds of entry:

    T(...)  a CODING TASK    "write a function to reverse a string"
    C(...)  a CONCEPT        "what is a list comprehension?"

Each T carries a `test`. build_data2.py runs every single one before any
training happens, so we never teach the model code that does not work.

The {v} inside the code is a placeholder for the parameter name. The same
task is generated with `s`, `text`, `word`... so the model learns the IDEA
rather than memorising one exact string. It is filled in with a plain
str.replace, not .format(), so real braces in the code need no escaping.

Run me:  python tasks.py        # prints the size of the curriculum
"""

import textwrap


def T(name, asks, code, why, test, vars=("x",)):
    """One coding task: what to ask for, the answer, why it works, and a proof."""
    return {
        "kind": "code",
        "name": name,
        "asks": asks,
        "code": textwrap.dedent(code).strip(),
        "why": " ".join(why.split()),
        "test": test,
        "vars": list(vars),
    }


def C(name, asks, answer):
    """One concept question: no code to run, just an explanation."""
    return {
        "kind": "concept",
        "name": name,
        "asks": asks,
        "answer": textwrap.dedent(answer).strip(),
    }


# ============================================================
# STRINGS
# ============================================================

STRINGS = [
    T("reverse_string",
      ["reverse a string", "flip a string backwards", "return a string in reverse order"],
      """
      def reverse_string({v}):
          return {v}[::-1]
      """,
      """Slicing with a step of -1 walks the string from the last character to
         the first, so it builds a brand new reversed string. Strings in Python
         cannot be changed in place, which is why this returns a new one.""",
      "assert reverse_string('hello') == 'olleh'",
      vars=["s", "text", "word"]),

    T("is_palindrome",
      ["check if a string is a palindrome", "test whether a word reads the same backwards",
       "detect palindromes"],
      """
      def is_palindrome({v}):
          cleaned = {v}.lower().replace(' ', '')
          return cleaned == cleaned[::-1]
      """,
      """We lowercase the text and drop the spaces first so that 'Never Odd Or
         Even' still counts. Then we simply compare the cleaned string with its
         own reverse. If they match, it is a palindrome.""",
      "assert is_palindrome('Never Odd Or Even') is True and is_palindrome('hello') is False",
      vars=["s", "text", "word"]),

    T("count_vowels",
      ["count the vowels in a string", "count how many vowels a word has",
       "find the number of vowels in some text"],
      """
      def count_vowels({v}):
          return sum(1 for ch in {v}.lower() if ch in 'aeiou')
      """,
      """We lowercase the text once so we do not have to check both cases. The
         generator inside sum yields a 1 for every character that appears in the
         string 'aeiou', and sum adds those ones up.""",
      "assert count_vowels('Programming') == 3",
      vars=["s", "text", "word"]),

    T("capitalize_words",
      ["capitalize every word in a sentence", "make the first letter of each word uppercase",
       "title case a sentence"],
      """
      def capitalize_words({v}):
          return ' '.join(word.capitalize() for word in {v}.split())
      """,
      """split() breaks the sentence into a list of words on whitespace,
         capitalize() uppercases the first letter of each one, and join glues
         them back together with single spaces between them.""",
      "assert capitalize_words('hello wide world') == 'Hello Wide World'",
      vars=["s", "sentence", "text"]),

    T("remove_spaces",
      ["remove all spaces from a string", "strip every space out of some text",
       "delete whitespace from a string"],
      """
      def remove_spaces({v}):
          return {v}.replace(' ', '')
      """,
      """replace swaps every occurrence of the first argument with the second.
         Replacing a space with an empty string simply deletes it. The original
         string is untouched because strings are immutable.""",
      "assert remove_spaces('a b c') == 'abc'",
      vars=["s", "text"]),

    T("count_words",
      ["count the words in a sentence", "find how many words are in a string",
       "get the word count of some text"],
      """
      def count_words({v}):
          return len({v}.split())
      """,
      """split() with no arguments splits on any run of whitespace and throws
         away empty pieces, so it handles double spaces and tabs correctly.
         len() then counts the items in the list it produced.""",
      "assert count_words('  the quick  brown fox ') == 4",
      vars=["s", "sentence", "text"]),

    T("longest_word",
      ["find the longest word in a sentence", "get the biggest word in some text"],
      """
      def longest_word({v}):
          return max({v}.split(), key=len)
      """,
      """max normally compares the items themselves, but key=len tells it to
         compare their lengths instead. It still returns the original word, not
         the length. If two words tie, the first one wins.""",
      "assert longest_word('a bb cccc dd') == 'cccc'",
      vars=["s", "sentence", "text"]),

    T("char_frequency",
      ["count how many times each character appears in a string",
       "build a frequency table of characters", "count letter occurrences"],
      """
      def char_frequency({v}):
          counts = {}
          for ch in {v}:
              counts[ch] = counts.get(ch, 0) + 1
          return counts
      """,
      """We walk the string one character at a time. get(ch, 0) returns the
         current count, or 0 the first time we have seen that character, so we
         never hit a KeyError. Then we store the count plus one.""",
      "assert char_frequency('aab') == {'a': 2, 'b': 1}",
      vars=["s", "text"]),

    T("starts_with_vowel",
      ["check if a word starts with a vowel", "test whether a string begins with a vowel"],
      """
      def starts_with_vowel({v}):
          return len({v}) > 0 and {v}[0].lower() in 'aeiou'
      """,
      """We check the length first so an empty string does not crash on index
         0. Python's `and` stops as soon as the left side is False, which is
         what makes that guard work.""",
      "assert starts_with_vowel('Apple') is True and starts_with_vowel('dog') is False",
      vars=["word", "s", "text"]),

    T("repeat_string",
      ["repeat a string n times", "duplicate some text a number of times"],
      """
      def repeat_string({v}, times):
          return {v} * times
      """,
      """Multiplying a string by an integer repeats it. It is the same operator
         you use for numbers, but Python gives it a different meaning for
         strings and lists.""",
      "assert repeat_string('ab', 3) == 'ababab'",
      vars=["s", "text"]),

    T("to_snake_case",
      ["convert a sentence to snake case", "turn text into snake_case"],
      """
      def to_snake_case({v}):
          return '_'.join({v}.lower().split())
      """,
      """Lowercase everything, split it into words on whitespace, then join the
         words back together with underscores instead of spaces.""",
      "assert to_snake_case('Hello Wide World') == 'hello_wide_world'",
      vars=["s", "text", "sentence"]),

    T("remove_punctuation",
      ["remove punctuation from a string", "strip out punctuation marks from text"],
      """
      def remove_punctuation({v}):
          import string
          return ''.join(ch for ch in {v} if ch not in string.punctuation)
      """,
      """string.punctuation is a ready-made string of every ASCII punctuation
         character. We keep only the characters that are not in it and join the
         survivors back into one string.""",
      "assert remove_punctuation('hi, there!') == 'hi there'",
      vars=["s", "text"]),

    T("count_substring",
      ["count how many times a substring appears in a string",
       "find the number of occurrences of a word in text"],
      """
      def count_substring({v}, piece):
          return {v}.count(piece)
      """,
      """count is built into every string. It counts non-overlapping matches,
         so 'aaa'.count('aa') is 1 and not 2 - worth knowing before you rely
         on it.""",
      "assert count_substring('banana', 'an') == 2",
      vars=["s", "text"]),

    T("is_anagram",
      ["check if two strings are anagrams", "test whether two words use the same letters"],
      """
      def is_anagram(first, second):
          return sorted(first.lower()) == sorted(second.lower())
      """,
      """Two words are anagrams when they contain exactly the same letters. If
         you sort both into alphabetical order, anagrams become identical
         lists, so a single == answers the question.""",
      "assert is_anagram('Listen', 'silent') is True"),

    T("truncate_string",
      ["truncate a string to a maximum length", "cut text short and add dots"],
      """
      def truncate_string({v}, limit):
          if len({v}) <= limit:
              return {v}
          return {v}[:limit - 3] + '...'
      """,
      """If the text already fits we return it untouched. Otherwise we keep
         room for the three dots by slicing to limit - 3, so the result is
         never longer than the limit you asked for.""",
      "assert truncate_string('abcdefghij', 8) == 'abcde...'",
      vars=["s", "text"]),

    T("swap_case",
      ["swap the case of every letter in a string", "make uppercase lowercase and vice versa"],
      """
      def swap_case({v}):
          return {v}.swapcase()
      """,
      """swapcase is already built into Python strings. It turns every
         uppercase letter lowercase and every lowercase letter uppercase, and
         leaves digits and symbols alone.""",
      "assert swap_case('Hello') == 'hELLO'",
      vars=["s", "text"]),

    T("first_non_repeating",
      ["find the first non repeating character in a string",
       "get the first character that appears only once"],
      """
      def first_non_repeating({v}):
          for ch in {v}:
              if {v}.count(ch) == 1:
                  return ch
          return None
      """,
      """We walk the string in order and return the first character whose total
         count is one. Returning None at the end covers the case where every
         character repeats.""",
      "assert first_non_repeating('aabbcdd') == 'c'",
      vars=["s", "text"]),

    T("string_to_list",
      ["split a comma separated string into a list", "turn csv text into a list of values"],
      """
      def string_to_list({v}):
          return [piece.strip() for piece in {v}.split(',')]
      """,
      """split(',') breaks the string at every comma. strip() then removes any
         leading or trailing spaces from each piece, which is what saves you
         when the input is written as 'a, b, c'.""",
      "assert string_to_list('a, b ,c') == ['a', 'b', 'c']",
      vars=["s", "text"]),
]


# ============================================================
# LISTS
# ============================================================

LISTS = [
    T("list_sum",
      ["add up all the numbers in a list", "sum a list of numbers", "total a list"],
      """
      def list_sum({v}):
          total = 0
          for number in {v}:
              total += number
          return total
      """,
      """We start a running total at zero and add each item to it as we walk
         the list. Python has a built-in sum() that does exactly this, but
         writing the loop shows you what sum is actually doing.""",
      "assert list_sum([1, 2, 3, 4]) == 10",
      vars=["numbers", "items", "values"]),

    T("list_average",
      ["find the average of a list of numbers", "calculate the mean of a list"],
      """
      def list_average({v}):
          if not {v}:
              return 0
          return sum({v}) / len({v})
      """,
      """The average is the total divided by how many items there are. The
         guard at the top matters: dividing by len([]) would raise
         ZeroDivisionError on an empty list.""",
      "assert list_average([2, 4, 6]) == 4.0",
      vars=["numbers", "values", "items"]),

    T("find_max",
      ["find the largest number in a list", "get the maximum value of a list without using max"],
      """
      def find_max({v}):
          biggest = {v}[0]
          for number in {v}[1:]:
              if number > biggest:
                  biggest = number
          return biggest
      """,
      """We assume the first item is the winner, then compare it against every
         other item and take over whenever we find something bigger. This is
         exactly how the built-in max() works internally.""",
      "assert find_max([3, 9, 2, 7]) == 9",
      vars=["numbers", "values", "items"]),

    T("remove_duplicates",
      ["remove duplicates from a list", "get the unique items of a list keeping order"],
      """
      def remove_duplicates({v}):
          seen = set()
          result = []
          for item in {v}:
              if item not in seen:
                  seen.add(item)
                  result.append(item)
          return result
      """,
      """A set remembers what we have already met and checks membership
         instantly. We append to the result only the first time we see each
         item, which is what preserves the original order.""",
      "assert remove_duplicates([1, 2, 1, 3, 2]) == [1, 2, 3]",
      vars=["items", "values", "numbers"]),

    T("flatten_list",
      ["flatten a list of lists", "turn a nested list into a flat one"],
      """
      def flatten_list({v}):
          result = []
          for inner in {v}:
              for item in inner:
                  result.append(item)
          return result
      """,
      """The outer loop walks the sub-lists and the inner loop walks the items
         inside each one. Note this only flattens one level deep - a list
         nested three deep would need recursion.""",
      "assert flatten_list([[1, 2], [3], [4, 5]]) == [1, 2, 3, 4, 5]",
      vars=["nested", "items", "lists"]),

    T("filter_even",
      ["filter the even numbers out of a list", "keep only the even numbers in a list"],
      """
      def filter_even({v}):
          return [number for number in {v} if number % 2 == 0]
      """,
      """This is a list comprehension with a filter. The `if` at the end
         decides which items survive, and % 2 == 0 is the standard test for
         evenness - the remainder after dividing by two is zero.""",
      "assert filter_even([1, 2, 3, 4, 5, 6]) == [2, 4, 6]",
      vars=["numbers", "values", "items"]),

    T("square_list",
      ["square every number in a list", "multiply each item in a list by itself"],
      """
      def square_list({v}):
          return [number * number for number in {v}]
      """,
      """A list comprehension builds a new list by running an expression on
         every item of the old one. The original list is not modified.""",
      "assert square_list([1, 2, 3]) == [1, 4, 9]",
      vars=["numbers", "values", "items"]),

    T("second_largest",
      ["find the second largest number in a list", "get the second biggest value"],
      """
      def second_largest({v}):
          unique = sorted(set({v}), reverse=True)
          return unique[1] if len(unique) > 1 else None
      """,
      """set() removes duplicates so that [5, 5, 3] correctly answers 3 and not
         5. We sort what is left from big to small and take index 1, returning
         None when there is no genuine second place.""",
      "assert second_largest([5, 5, 3, 9]) == 5",
      vars=["numbers", "values", "items"]),

    T("chunk_list",
      ["split a list into chunks of a given size", "break a list into equal groups"],
      """
      def chunk_list({v}, size):
          return [{v}[i:i + size] for i in range(0, len({v}), size)]
      """,
      """range with a step of `size` gives us the start index of every chunk:
         0, size, 2*size and so on. Slicing past the end of a list is safe in
         Python, so the final short chunk needs no special case.""",
      "assert chunk_list([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]",
      vars=["items", "values", "numbers"]),

    T("merge_lists",
      ["merge two lists into one", "combine two lists together"],
      """
      def merge_lists(first, second):
          return first + second
      """,
      """The + operator on two lists creates a brand new list holding the items
         of both. Neither input list is changed. Use first.extend(second) if
         you do want to modify the first one in place.""",
      "assert merge_lists([1, 2], [3]) == [1, 2, 3]"),

    T("common_items",
      ["find the items that appear in both lists", "get the intersection of two lists"],
      """
      def common_items(first, second):
          return sorted(set(first) & set(second))
      """,
      """The & operator on two sets gives their intersection - the items that
         appear in both. We sort the result so the output is predictable,
         because sets have no order of their own.""",
      "assert common_items([1, 2, 3], [2, 3, 4]) == [2, 3]"),

    T("count_occurrences",
      ["count how many times a value appears in a list", "count occurrences in a list"],
      """
      def count_occurrences({v}, target):
          return {v}.count(target)
      """,
      """Lists have a built-in count method that walks the list and tallies the
         items equal to what you passed. It returns 0 rather than raising if
         the value is never found.""",
      "assert count_occurrences([1, 2, 2, 3], 2) == 2",
      vars=["items", "values", "numbers"]),

    T("sort_by_length",
      ["sort a list of words by length", "order strings from shortest to longest"],
      """
      def sort_by_length({v}):
          return sorted({v}, key=len)
      """,
      """sorted returns a new sorted list. key=len tells it to compare the
         lengths rather than the words themselves. Python's sort is stable, so
         words of equal length keep their original order.""",
      "assert sort_by_length(['ccc', 'a', 'bb']) == ['a', 'bb', 'ccc']",
      vars=["words", "items", "values"]),

    T("reverse_list",
      ["reverse a list", "put a list in the opposite order"],
      """
      def reverse_list({v}):
          return {v}[::-1]
      """,
      """The same slice trick that reverses a string reverses a list, because
         both are sequences. This returns a new list; {v}.reverse() would flip
         the original in place and return None.""",
      "assert reverse_list([1, 2, 3]) == [3, 2, 1]",
      vars=["items", "values", "numbers"]),

    T("rotate_list",
      ["rotate a list to the left by n places", "shift the items of a list around"],
      """
      def rotate_list({v}, n):
          if not {v}:
              return []
          n = n % len({v})
          return {v}[n:] + {v}[:n]
      """,
      """We cut the list at position n and swap the two halves. Taking n modulo
         the length means rotating by 7 on a list of 3 behaves exactly like
         rotating by 1.""",
      "assert rotate_list([1, 2, 3, 4], 1) == [2, 3, 4, 1]",
      vars=["items", "values", "numbers"]),

    T("zip_lists",
      ["pair up two lists into tuples", "zip two lists together"],
      """
      def zip_lists(first, second):
          return list(zip(first, second))
      """,
      """zip walks both lists in step and hands back a tuple from each
         position. It stops at the shorter list, so nothing ever goes out of
         range. zip is lazy, which is why we wrap it in list().""",
      "assert zip_lists([1, 2], ['a', 'b']) == [(1, 'a'), (2, 'b')]"),

    T("running_total",
      ["build a running total of a list", "make a cumulative sum list"],
      """
      def running_total({v}):
          result = []
          total = 0
          for number in {v}:
              total += number
              result.append(total)
          return result
      """,
      """We keep one accumulator outside the loop and append its current value
         after every addition. That is the difference between a running total
         and a plain sum: we record every step, not just the end.""",
      "assert running_total([1, 2, 3]) == [1, 3, 6]",
      vars=["numbers", "values", "items"]),

    T("is_sorted",
      ["check whether a list is sorted", "test if a list is in ascending order"],
      """
      def is_sorted({v}):
          return all({v}[i] <= {v}[i + 1] for i in range(len({v}) - 1))
      """,
      """We compare each item with the one after it. all() is True when every
         comparison holds, and it stops early at the first failure. An empty
         or single-item list is sorted by definition, which this handles.""",
      "assert is_sorted([1, 2, 2, 5]) is True and is_sorted([3, 1]) is False",
      vars=["items", "values", "numbers"]),

    T("bubble_sort",
      ["write a bubble sort", "sort a list using bubble sort"],
      """
      def bubble_sort({v}):
          items = list({v})
          for i in range(len(items)):
              for j in range(len(items) - 1 - i):
                  if items[j] > items[j + 1]:
                      items[j], items[j + 1] = items[j + 1], items[j]
          return items
      """,
      """Each pass walks the list swapping neighbours that are in the wrong
         order, which floats the largest remaining value to the end. After i
         passes the last i items are final, so the inner loop shrinks.""",
      "assert bubble_sort([3, 1, 2]) == [1, 2, 3]",
      vars=["numbers", "values", "items"]),

    T("binary_search",
      ["write a binary search", "search a sorted list efficiently"],
      """
      def binary_search({v}, target):
          low, high = 0, len({v}) - 1
          while low <= high:
              mid = (low + high) // 2
              if {v}[mid] == target:
                  return mid
              if {v}[mid] < target:
                  low = mid + 1
              else:
                  high = mid - 1
          return -1
      """,
      """We look at the middle of the range and throw away the half that cannot
         contain the target. Halving the search space every step is why this
         finds an item in a million-item list in about twenty comparisons. The
         list must already be sorted for it to work.""",
      "assert binary_search([1, 3, 5, 7, 9], 7) == 3",
      vars=["items", "values", "numbers"]),
]


# ============================================================
# NUMBERS AND MATH
# ============================================================

NUMBERS = [
    T("is_even",
      ["check if a number is even", "test whether a number is divisible by two"],
      """
      def is_even({v}):
          return {v} % 2 == 0
      """,
      """The % operator gives the remainder of a division. A number divided by
         two leaves a remainder of zero exactly when it is even, so the
         comparison itself is already the True or False answer.""",
      "assert is_even(4) is True and is_even(7) is False",
      vars=["n", "number", "value"]),

    T("factorial",
      ["calculate the factorial of a number", "compute n factorial"],
      """
      def factorial({v}):
          result = 1
          for i in range(2, {v} + 1):
              result *= i
          return result
      """,
      """Factorial means multiplying every whole number from 1 up to n. We
         start the result at 1 so that factorial(0) correctly returns 1, and
         the loop simply never runs in that case.""",
      "assert factorial(5) == 120 and factorial(0) == 1",
      vars=["n", "number"]),

    T("fibonacci",
      ["generate the fibonacci sequence", "print the first n fibonacci numbers"],
      """
      def fibonacci({v}):
          sequence = []
          a, b = 0, 1
          for _ in range({v}):
              sequence.append(a)
              a, b = b, a + b
          return sequence
      """,
      """Each Fibonacci number is the sum of the two before it. We hold those
         two in a and b and slide the window forward with a single tuple
         assignment, so no temporary variable is needed.""",
      "assert fibonacci(7) == [0, 1, 1, 2, 3, 5, 8]",
      vars=["n", "count"]),

    T("is_prime",
      ["check if a number is prime", "test whether a number has any divisors"],
      """
      def is_prime({v}):
          if {v} < 2:
              return False
          for i in range(2, int({v} ** 0.5) + 1):
              if {v} % i == 0:
                  return False
          return True
      """,
      """A prime has no divisors other than 1 and itself. We only need to test
         up to the square root, because any factor larger than that must pair
         with one smaller than it, which we would already have found.""",
      "assert is_prime(29) is True and is_prime(28) is False",
      vars=["n", "number"]),

    T("sum_of_digits",
      ["add up the digits of a number", "find the digit sum of an integer"],
      """
      def sum_of_digits({v}):
          return sum(int(digit) for digit in str(abs({v})))
      """,
      """Turning the number into a string lets us walk it digit by digit. abs()
         drops a minus sign so it does not become a digit, and int() turns each
         character back into a number before summing.""",
      "assert sum_of_digits(-1234) == 10",
      vars=["n", "number"]),

    T("gcd",
      ["find the greatest common divisor of two numbers", "compute the gcd"],
      """
      def gcd(a, b):
          while b:
              a, b = b, a % b
          return a
      """,
      """This is Euclid's algorithm, over two thousand years old. Replace the
         pair with (b, a mod b) repeatedly; when b hits zero, a is the greatest
         common divisor. It is startlingly fast.""",
      "assert gcd(48, 18) == 6"),

    T("celsius_to_fahrenheit",
      ["convert celsius to fahrenheit", "write a temperature converter"],
      """
      def celsius_to_fahrenheit({v}):
          return {v} * 9 / 5 + 32
      """,
      """This is the standard conversion formula. Note that in Python 3 the
         single slash always produces a float, so 100 * 9 / 5 gives 180.0 and
         not 180.""",
      "assert celsius_to_fahrenheit(100) == 212.0",
      vars=["celsius", "c", "temp"]),

    T("power",
      ["raise a number to a power without using the ** operator",
       "write my own exponent function"],
      """
      def power(base, exponent):
          result = 1
          for _ in range(exponent):
              result *= base
          return result
      """,
      """Raising to a power is just repeated multiplication. We start at 1 and
         multiply by the base once per exponent, which also makes anything to
         the power of zero come out as 1 for free.""",
      "assert power(2, 10) == 1024"),

    T("count_digits",
      ["count the digits in a number", "find how many digits an integer has"],
      """
      def count_digits({v}):
          return len(str(abs({v})))
      """,
      """Converting to a string and taking its length is the shortest honest
         way to do this. abs() first, otherwise the minus sign would be counted
         as a digit.""",
      "assert count_digits(-4071) == 4",
      vars=["n", "number"]),

    T("average_of_two",
      ["find the average of two numbers", "get the midpoint of two values"],
      """
      def average_of_two(a, b):
          return (a + b) / 2
      """,
      """Add the two numbers and halve the result. The brackets matter: without
         them Python would divide only b by 2 first, because division binds
         tighter than addition.""",
      "assert average_of_two(3, 8) == 5.5"),

    T("absolute_value",
      ["get the absolute value of a number without using abs",
       "make a number positive"],
      """
      def absolute_value({v}):
          return {v} if {v} >= 0 else -{v}
      """,
      """A conditional expression: the value before `if` is used when the test
         passes, otherwise the value after `else`. Negating a negative number
         makes it positive.""",
      "assert absolute_value(-7) == 7 and absolute_value(7) == 7",
      vars=["n", "number", "value"]),

    T("round_to_places",
      ["round a number to two decimal places", "format a float to n decimals"],
      """
      def round_to_places({v}, places=2):
          return round({v}, places)
      """,
      """round takes an optional second argument for how many decimal places to
         keep. Be aware it uses banker's rounding, so round(2.5) is 2 - use the
         decimal module if you need money-exact behaviour.""",
      "assert round_to_places(3.14159) == 3.14",
      vars=["value", "number", "n"]),

    T("is_leap_year",
      ["check if a year is a leap year", "test for leap years"],
      """
      def is_leap_year({v}):
          return {v} % 4 == 0 and ({v} % 100 != 0 or {v} % 400 == 0)
      """,
      """A year is a leap year if it divides by 4, except centuries, unless
         that century also divides by 400. That is why 1900 was not a leap year
         but 2000 was.""",
      "assert is_leap_year(2000) is True and is_leap_year(1900) is False",
      vars=["year", "y"]),

    T("multiplication_table",
      ["print a multiplication table", "show the times table for a number"],
      """
      def multiplication_table({v}, upto=10):
          lines = []
          for i in range(1, upto + 1):
              product = {v} * i
              lines.append(f'{{v}} x {i} = {product}')
          return lines
      """,
      """f-strings let you drop an expression straight inside the braces, and
         Python evaluates it and formats the result. We return the lines as a
         list so the caller decides whether to print them.""",
      "assert multiplication_table(3, 2) == ['3 x 1 = 3', '3 x 2 = 6']",
      vars=["n", "number"]),

    T("sum_to_n",
      ["add up all the numbers from 1 to n", "sum the first n whole numbers"],
      """
      def sum_to_n({v}):
          return {v} * ({v} + 1) // 2
      """,
      """Gauss's formula. Instead of looping n times we compute the answer in
         one step. The double slash is integer division, which keeps the result
         a whole number since n * (n + 1) is always even.""",
      "assert sum_to_n(100) == 5050",
      vars=["n", "number"]),

    T("min_and_max",
      ["find both the smallest and largest number in a list", "return the min and max together"],
      """
      def min_and_max({v}):
          return min({v}), max({v})
      """,
      """Returning two values separated by a comma actually returns one tuple.
         The caller can unpack it straight into two variables with
         `low, high = min_and_max(data)`.""",
      "assert min_and_max([4, 1, 9]) == (1, 9)",
      vars=["numbers", "values", "items"]),

    T("percentage",
      ["calculate what percentage one number is of another", "work out a percentage"],
      """
      def percentage(part, whole):
          if whole == 0:
              return 0
          return part / whole * 100
      """,
      """Divide the part by the whole to get a fraction, then multiply by 100.
         The guard stops a ZeroDivisionError when the whole is zero.""",
      "assert percentage(25, 200) == 12.5"),

    T("fizzbuzz",
      ["write fizzbuzz", "solve the fizzbuzz problem"],
      """
      def fizzbuzz({v}):
          result = []
          for i in range(1, {v} + 1):
              if i % 15 == 0:
                  result.append('FizzBuzz')
              elif i % 3 == 0:
                  result.append('Fizz')
              elif i % 5 == 0:
                  result.append('Buzz')
              else:
                  result.append(str(i))
          return result
      """,
      """The trick is testing 15 first. A number divisible by both 3 and 5 is
         divisible by 15, and if you check 3 before 15 you print 'Fizz' and
         never reach the combined case.""",
      "assert fizzbuzz(5) == ['1', '2', 'Fizz', '4', 'Buzz']",
      vars=["n", "limit"]),
]


# ============================================================
# DICTIONARIES AND SETS
# ============================================================

DICTS = [
    T("invert_dict",
      ["swap the keys and values of a dictionary", "invert a dict"],
      """
      def invert_dict({v}):
          return {value: key for key, value in {v}.items()}
      """,
      """A dict comprehension builds a new dictionary. items() hands us each
         key and value as a pair, and we write them back the other way round.
         Duplicate values collapse, because keys must be unique.""",
      "assert invert_dict({'a': 1, 'b': 2}) == {1: 'a', 2: 'b'}",
      vars=["mapping", "d", "data"]),

    T("merge_dicts",
      ["merge two dictionaries", "combine two dicts into one"],
      """
      def merge_dicts(first, second):
          return {**first, **second}
      """,
      """The ** operator unpacks a dictionary into another one. When both dicts
         hold the same key the later one wins, so `second` overrides `first`.""",
      "assert merge_dicts({'a': 1}, {'b': 2, 'a': 9}) == {'a': 9, 'b': 2}"),

    T("dict_max_value",
      ["find the key with the largest value in a dictionary",
       "get the highest scoring key of a dict"],
      """
      def dict_max_value({v}):
          return max({v}, key={v}.get)
      """,
      """Looping over a dict gives you its keys, and key={v}.get tells max to
         judge each key by the value it maps to. What comes back is the key
         itself, which is usually what you actually wanted.""",
      "assert dict_max_value({'a': 3, 'b': 9}) == 'b'",
      vars=["scores", "d", "data"]),

    T("sort_dict_by_value",
      ["sort a dictionary by its values", "order a dict from lowest value to highest"],
      """
      def sort_dict_by_value({v}):
          return dict(sorted({v}.items(), key=lambda pair: pair[1]))
      """,
      """items() gives (key, value) pairs. The lambda picks element 1 of each
         pair - the value - as the thing to sort on. Since Python 3.7
         dictionaries keep their insertion order, so the new dict stays
         sorted.""",
      "assert sort_dict_by_value({'a': 3, 'b': 1}) == {'b': 1, 'a': 3}",
      vars=["scores", "d", "data"]),

    T("dict_get_safe",
      ["read a dictionary key without crashing if it is missing",
       "safely look up a key in a dict"],
      """
      def dict_get_safe({v}, key, default=None):
          return {v}.get(key, default)
      """,
      """Square brackets raise KeyError when the key is absent. get() returns
         the default instead, which is None unless you say otherwise. Use it
         whenever the key is genuinely optional.""",
      "assert dict_get_safe({'a': 1}, 'z', 0) == 0",
      vars=["d", "data", "mapping"]),

    T("count_items",
      ["count how many times each item appears in a list",
       "build a tally of a list using a dictionary"],
      """
      def count_items({v}):
          counts = {}
          for item in {v}:
              counts[item] = counts.get(item, 0) + 1
          return counts
      """,
      """The same get-with-a-default trick that makes character counting safe.
         collections.Counter does this in one line, but this version shows you
         what Counter is doing under the hood.""",
      "assert count_items(['a', 'b', 'a']) == {'a': 2, 'b': 1}",
      vars=["items", "values", "words"]),

    T("filter_dict",
      ["keep only the dictionary entries above a value",
       "filter a dict by its values"],
      """
      def filter_dict({v}, minimum):
          return {key: value for key, value in {v}.items() if value >= minimum}
      """,
      """A dict comprehension with a condition. Every pair that fails the test
         is simply left out of the new dictionary. The original is not
         changed.""",
      "assert filter_dict({'a': 1, 'b': 5}, 3) == {'b': 5}",
      vars=["scores", "d", "data"]),

    T("group_by_length",
      ["group a list of words by their length", "bucket words into a dictionary by length"],
      """
      def group_by_length({v}):
          groups = {}
          for word in {v}:
              groups.setdefault(len(word), []).append(word)
          return groups
      """,
      """setdefault returns the list stored under that key, creating an empty
         one first if the key is new. That lets us append in a single line
         without checking whether the bucket already exists.""",
      "assert group_by_length(['hi', 'be', 'sun']) == {2: ['hi', 'be'], 3: ['sun']}",
      vars=["words", "items", "values"]),

    T("unique_items",
      ["get the unique values from a list using a set", "remove duplicates with a set"],
      """
      def unique_items({v}):
          return sorted(set({v}))
      """,
      """A set physically cannot hold the same value twice, so building one
         removes duplicates instantly. Sets have no order, which is why we sort
         before returning so the answer is predictable.""",
      "assert unique_items([3, 1, 3, 2]) == [1, 2, 3]",
      vars=["items", "values", "numbers"]),

    T("dict_to_list_of_pairs",
      ["turn a dictionary into a list of key value pairs", "get a dict as tuples"],
      """
      def dict_to_list_of_pairs({v}):
          return list({v}.items())
      """,
      """items() gives a live view of the dictionary, not a real list, which is
         why we wrap it in list(). Each element is a (key, value) tuple.""",
      "assert dict_to_list_of_pairs({'a': 1}) == [('a', 1)]",
      vars=["d", "data", "mapping"]),
]


# ============================================================
# FILES AND INPUT / OUTPUT
# ============================================================

FILES = [
    T("read_file",
      ["read a text file", "open a file and get its contents"],
      """
      def read_file(path):
          with open(path, 'r', encoding='utf-8') as handle:
              return handle.read()
      """,
      """The `with` block guarantees the file is closed even if an error is
         raised inside it. Always pass encoding='utf-8' explicitly - the
         default depends on the operating system and will bite you on
         Windows.""",
      "assert callable(read_file)"),

    T("write_file",
      ["write text to a file", "save a string to disk"],
      """
      def write_file(path, {v}):
          with open(path, 'w', encoding='utf-8') as handle:
              handle.write({v})
      """,
      """Mode 'w' creates the file, or empties it completely if it already
         exists. Use 'a' instead if you want to add to the end rather than
         replace what is there.""",
      "assert callable(write_file)",
      vars=["text", "content", "data"]),

    T("read_lines",
      ["read a file into a list of lines", "get every line of a file"],
      """
      def read_lines(path):
          with open(path, 'r', encoding='utf-8') as handle:
              return [line.rstrip('\\n') for line in handle]
      """,
      """Looping over a file object yields one line at a time without loading
         the whole file into memory. rstrip removes the trailing newline that
         each line still carries.""",
      "assert callable(read_lines)"),

    T("append_to_file",
      ["append a line to a file", "add text to the end of a file"],
      """
      def append_to_file(path, line):
          with open(path, 'a', encoding='utf-8') as handle:
              handle.write(line + '\\n')
      """,
      """Mode 'a' means append: writing starts at the end of the existing
         content. We add the newline ourselves because write does not add one
         for you, unlike print.""",
      "assert callable(append_to_file)"),

    T("file_exists",
      ["check if a file exists", "test whether a path is there before opening it"],
      """
      def file_exists(path):
          import os
          return os.path.exists(path)
      """,
      """os.path.exists returns True for files and folders alike. If you need
         to be sure it is a file and not a directory, use os.path.isfile
         instead.""",
      "assert file_exists('.') is True"),

    T("read_json",
      ["read a json file", "load json from disk into a dictionary"],
      """
      def read_json(path):
          import json
          with open(path, 'r', encoding='utf-8') as handle:
              return json.load(handle)
      """,
      """json.load reads from a file object and hands back Python dicts and
         lists. Its cousin json.loads takes a string instead - the extra s
         stands for string, and mixing them up is a common slip.""",
      "assert callable(read_json)"),

    T("write_json",
      ["write a dictionary to a json file", "save data as json"],
      """
      def write_json(path, {v}):
          import json
          with open(path, 'w', encoding='utf-8') as handle:
              json.dump({v}, handle, indent=2)
      """,
      """json.dump writes straight to the file. indent=2 makes the output
         readable by a human instead of one enormous line, which is worth the
         extra bytes for config files.""",
      "assert callable(write_json)",
      vars=["data", "content", "records"]),

    T("count_lines_in_file",
      ["count the lines in a file", "find how many lines a text file has"],
      """
      def count_lines_in_file(path):
          with open(path, 'r', encoding='utf-8') as handle:
              return sum(1 for _ in handle)
      """,
      """We add one for every line the file yields, without ever holding more
         than a single line in memory. That matters when the file is bigger
         than your RAM.""",
      "assert callable(count_lines_in_file)"),
]


# ============================================================
# FUNCTIONS, CLASSES, AND PYTHON MACHINERY
# ============================================================

PYTHON = [
    T("simple_class",
      ["write a simple class", "create a class with an init method", "make a Person class"],
      """
      class Person:
          def __init__(self, name, age):
              self.name = name
              self.age = age

          def greet(self):
              return f'Hi, I am {self.name}'
      """,
      """__init__ runs the moment you create the object and stores the data on
         self. `self` is just the object itself, handed to every method
         automatically as the first argument.""",
      "assert Person('Ada', 36).greet() == 'Hi, I am Ada'"),

    T("class_with_str",
      ["make a class print nicely", "add a string representation to a class"],
      """
      class Point:
          def __init__(self, x, y):
              self.x = x
              self.y = y

          def __str__(self):
              return f'Point({self.x}, {self.y})'
      """,
      """__str__ is what print() and str() call. Without it you get the ugly
         default like <__main__.Point object at 0x7f...>, which tells you
         nothing useful while debugging.""",
      "assert str(Point(1, 2)) == 'Point(1, 2)'"),

    T("class_inheritance",
      ["write a class that inherits from another", "show inheritance in python"],
      """
      class Animal:
          def __init__(self, name):
              self.name = name

          def speak(self):
              return '...'

      class Dog(Animal):
          def speak(self):
              return 'Woof'
      """,
      """Dog(Animal) means Dog gets everything Animal has. It reuses Animal's
         __init__ without rewriting it, and replaces only the speak method.
         That replacement is called overriding.""",
      "assert Dog('Rex').speak() == 'Woof' and Dog('Rex').name == 'Rex'"),

    T("default_argument",
      ["write a function with a default argument", "make a parameter optional"],
      """
      def greet(name, greeting='Hello'):
          return f'{greeting}, {name}!'
      """,
      """Parameters with a default can be left out by the caller. They must
         come after the ones without a default. Never use a list or dict as a
         default value - it is created once and shared between calls.""",
      "assert greet('Sam') == 'Hello, Sam!' and greet('Sam', 'Hi') == 'Hi, Sam!'"),

    T("args_kwargs",
      ["write a function that takes any number of arguments", "explain args and kwargs"],
      """
      def show(*args, **kwargs):
          return list(args), dict(kwargs)
      """,
      """*args collects any extra positional arguments into a tuple, and
         **kwargs collects any extra named ones into a dictionary. The stars
         are what matter; the names args and kwargs are only convention.""",
      "assert show(1, 2, mode='fast') == ([1, 2], {'mode': 'fast'})"),

    T("lambda_function",
      ["write a lambda function", "make a one line anonymous function"],
      """
      double = lambda {v}: {v} * 2
      """,
      """A lambda is a function with no name and a single expression, which is
         automatically returned. It is handy as a `key=` argument. For anything
         longer, a normal def is clearer and easier to debug.""",
      "assert double(5) == 10",
      vars=["n", "x", "value"]),

    T("decorator",
      ["write a decorator", "make a function that wraps another function"],
      """
      def shout(func):
          def wrapper(*args, **kwargs):
              return func(*args, **kwargs).upper()
          return wrapper

      @shout
      def hello(name):
          return f'hello {name}'
      """,
      """A decorator takes a function and returns a replacement for it. The
         @shout line is shorthand for hello = shout(hello). *args and **kwargs
         let the wrapper pass through whatever arguments the original takes.""",
      "assert hello('sam') == 'HELLO SAM'"),

    T("generator_function",
      ["write a generator", "use yield instead of return"],
      """
      def countdown({v}):
          while {v} > 0:
              yield {v}
              {v} -= 1
      """,
      """yield hands one value back and freezes the function where it stands.
         The next time you ask for a value it carries on from that exact line.
         Nothing is stored, so a generator can be endless.""",
      "assert list(countdown(3)) == [3, 2, 1]",
      vars=["n", "start", "count"]),

    T("recursion",
      ["write a recursive function", "solve factorial with recursion"],
      """
      def factorial_recursive({v}):
          if {v} <= 1:
              return 1
          return {v} * factorial_recursive({v} - 1)
      """,
      """A recursive function calls itself on a smaller problem. The `if` at
         the top is the base case, and without it the calls never stop and
         Python raises RecursionError.""",
      "assert factorial_recursive(5) == 120",
      vars=["n", "number"]),

    T("enumerate_loop",
      ["loop over a list with the index", "get the position while looping"],
      """
      def numbered({v}):
          return [f'{i}: {item}' for i, item in enumerate({v})]
      """,
      """enumerate wraps any sequence and yields (index, item) pairs. It saves
         you from the clumsy `for i in range(len(items))` and keeps the item
         itself right there in the loop.""",
      "assert numbered(['a', 'b']) == ['0: a', '1: b']",
      vars=["items", "values", "words"]),

    T("try_except",
      ["handle an error with try except", "catch an exception in python"],
      """
      def safe_divide(a, b):
          try:
              return a / b
          except ZeroDivisionError:
              return None
      """,
      """The code in try runs normally; if the named error is raised, control
         jumps to except instead of crashing. Always catch a specific
         exception. A bare `except:` also swallows your typos.""",
      "assert safe_divide(10, 2) == 5.0 and safe_divide(1, 0) is None"),

    T("raise_error",
      ["raise an exception on bad input", "validate an argument and raise an error"],
      """
      def set_age({v}):
          if {v} < 0:
              raise ValueError('age cannot be negative')
          return {v}
      """,
      """Raising an error stops the function immediately and hands the problem
         to the caller. That is better than silently returning None, because a
         wrong value would travel through your program undetected.""",
      "assert set_age(30) == 30",
      vars=["age", "value", "n"]),

    T("list_to_string",
      ["join a list of strings into one sentence", "convert a list into a string"],
      """
      def list_to_string({v}, separator=' '):
          return separator.join(str(item) for item in {v})
      """,
      """join is a method on the separator, not on the list, which surprises
         everyone once. We wrap each item in str() so a list of numbers does
         not raise a TypeError.""",
      "assert list_to_string([1, 2, 3], '-') == '1-2-3'",
      vars=["items", "values", "words"]),

    T("swap_variables",
      ["swap two variables", "exchange the values of two variables"],
      """
      def swap(a, b):
          a, b = b, a
          return a, b
      """,
      """Python builds a tuple of the right-hand side first, then unpacks it
         into the names on the left. That is why no temporary variable is
         needed and why this cannot go wrong.""",
      "assert swap(1, 2) == (2, 1)"),

    T("map_and_filter",
      ["use map and filter", "apply a function to every item and keep some"],
      """
      def evens_doubled({v}):
          return list(map(lambda n: n * 2, filter(lambda n: n % 2 == 0, {v})))
      """,
      """filter keeps the items where the function returns True, and map runs a
         function over whatever is left. Both are lazy, so list() is what
         actually makes the work happen.""",
      "assert evens_doubled([1, 2, 3, 4]) == [4, 8]",
      vars=["numbers", "values", "items"]),

    T("dataclass_example",
      ["use a dataclass", "make a simple data holding class quickly"],
      """
      from dataclasses import dataclass

      @dataclass
      class Book:
          title: str
          pages: int = 0
      """,
      """@dataclass writes __init__, __repr__ and __eq__ for you from the
         annotations. You get a class that prints nicely and compares by value
         instead of by identity, in four lines.""",
      "assert Book('Dune', 412) == Book('Dune', 412)"),

    T("static_method",
      ["add a method to a class that does not use self", "write a static method"],
      """
      class MathHelper:
          @staticmethod
          def add(a, b):
              return a + b
      """,
      """@staticmethod means the method needs nothing from the object, so it
         does not take self. You can call it straight on the class:
         MathHelper.add(2, 3).""",
      "assert MathHelper.add(2, 3) == 5"),

    T("property_decorator",
      ["make a computed attribute on a class", "use the property decorator"],
      """
      class Rectangle:
          def __init__(self, width, height):
              self.width = width
              self.height = height

          @property
          def area(self):
              return self.width * self.height
      """,
      """@property turns a method into something you read like a plain
         attribute: rect.area, with no brackets. The value is recalculated
         every time, so it can never fall out of date.""",
      "assert Rectangle(3, 4).area == 12"),
]


# ============================================================
# BUGS - the same tasks, but broken. Used for "fix this code".
# ============================================================
# Each one is a realistic beginner mistake with a one-line explanation of
# what actually went wrong. build_data2.py pairs the broken code with the
# correct version from the tables above.

BUGS = [
    ("missing_return",
     "The function calculates the answer but never returns it, so it hands "
     "back None. Adding the `return` keyword fixes it."),
    ("assignment_in_condition",
     "A single = assigns a value, while == compares two values. The condition "
     "needs the double equals."),
    ("off_by_one",
     "range(1, n) stops one short because range never includes its end value. "
     "It needs range(1, n + 1) to reach n itself."),
    ("wrong_indent",
     "The return sits inside the loop, so the function exits on the very first "
     "pass. Un-indenting it lets the loop finish first."),
]


# ============================================================
# CONCEPTS - questions with no code to run
# ============================================================

CONCEPTS = [
    C("list_comprehension",
      ["what is a list comprehension", "explain list comprehensions",
       "how do list comprehensions work"],
      """
      A list comprehension builds a whole list in one expression, instead of
      creating an empty list and appending to it in a loop.

      ```python
      squares = [n * n for n in range(5)]
      ```

      That gives [0, 1, 4, 9, 16]. You can add a filter on the end with `if`,
      and the same syntax works for dictionaries and sets. Keep them to one
      line - a comprehension with three nested loops is harder to read than
      the loop it replaced."""),

    C("list_vs_tuple",
      ["what is the difference between a list and a tuple",
       "when should i use a tuple instead of a list",
       "explain lists versus tuples"],
      """
      A list can be changed after it is created; a tuple cannot.

      ```python
      colours = ['red', 'blue']    # can append, remove, reorder
      point = (3, 4)               # fixed forever
      ```

      Because tuples never change they can be used as dictionary keys, and
      they are slightly faster. Use a tuple when the number of items is part
      of the meaning, like a coordinate, and a list when you are collecting
      things."""),

    C("what_is_a_function",
      ["what is a function", "why should i write functions",
       "explain functions in python"],
      """
      A function is a named block of code that takes inputs and gives back a
      result, so you can run it as many times as you like without repeating
      yourself.

      ```python
      def area(width, height):
          return width * height
      ```

      The real win is not saving typing. It is that a bug in `area` has
      exactly one place to be fixed, and the name tells the next reader what
      the code is for."""),

    C("what_is_a_dictionary",
      ["what is a dictionary", "explain python dictionaries", "what is a dict used for"],
      """
      A dictionary stores values under keys, so you look things up by name
      rather than by position.

      ```python
      ages = {'Ada': 36, 'Linus': 54}
      print(ages['Ada'])
      ```

      Lookups are effectively instant no matter how big the dictionary gets,
      which is why dicts are everywhere in Python. Keys must be immutable -
      strings, numbers and tuples work; lists do not."""),

    C("what_is_a_set",
      ["what is a set in python", "when should i use a set",
       "explain sets in python"],
      """
      A set is an unordered collection that cannot hold the same value twice.

      ```python
      seen = {1, 2, 2, 3}     # becomes {1, 2, 3}
      ```

      Two things make sets useful: they remove duplicates for free, and
      `x in my_set` is instant even for a million items, while `x in my_list`
      has to walk the whole list."""),

    C("mutable_vs_immutable",
      ["what does mutable mean", "what is the difference between mutable and immutable",
       "explain mutability in python"],
      """
      Mutable means the object can be changed in place. Immutable means it
      cannot, so any "change" actually creates a new object.

      Lists, dicts and sets are mutable. Strings, numbers and tuples are not.

      ```python
      s = 'hi'
      s.upper()      # returns 'HI', s is still 'hi'
      ```

      This is why string methods always return a new string, and why passing
      a list into a function can modify the caller's list."""),

    C("what_is_a_loop",
      ["what is a for loop", "explain loops in python", "how does a for loop work"],
      """
      A for loop runs the same block of code once for every item in a
      sequence.

      ```python
      for name in ['Ada', 'Grace']:
          print(name)
      ```

      Python's for loop walks items directly, unlike C-style languages where
      you manage a counter. If you need the position too, wrap the sequence in
      enumerate()."""),

    C("while_vs_for",
      ["what is the difference between a while loop and a for loop",
       "when should i use while instead of for",
       "explain the two kinds of loop"],
      """
      Use `for` when you know what you are looping over - a list, a range, the
      lines of a file. Use `while` when you are looping until a condition
      changes and you cannot say in advance how many times that will take.

      ```python
      while not finished:
          finished = do_one_step()
      ```

      Every while loop needs something inside it that can eventually make the
      condition False, or it runs forever."""),

    C("what_is_a_class",
      ["what is a class", "explain classes and objects", "what is object oriented programming"],
      """
      A class is a blueprint. An object is one thing built from that
      blueprint, holding its own data.

      ```python
      class Dog:
          def __init__(self, name):
              self.name = name

      rex = Dog('Rex')
      ```

      Classes are worth it when data and the behaviour that acts on it belong
      together. If you only ever store data, a dataclass or a dictionary is
      usually simpler."""),

    C("what_is_self",
      ["what does self mean in python", "why do methods take self",
       "explain self in a class"],
      """
      `self` is the object the method was called on. Python passes it in
      automatically, which is why you write `rex.speak()` but define
      `def speak(self)`.

      Anything you store on self belongs to that one object, so two Dogs can
      each have their own name. The name `self` is only a convention, but
      breaking it will confuse every Python programmer who reads your code."""),

    C("what_is_none",
      ["what is none in python", "explain none",
       "when do i get none back"],
      """
      None is Python's way of saying "no value here". It is not zero and not
      an empty string - it is its own thing.

      A function with no return statement returns None automatically, which is
      the usual reason you see `NoneType` in an error message.

      Compare with `is`, not `==`:

      ```python
      if result is None:
          ...
      ```"""),

    C("what_is_an_exception",
      ["what is an exception", "explain errors and exceptions in python",
       "how do i handle errors"],
      """
      An exception is Python stopping and saying it cannot carry on: a missing
      file, a division by zero, a key that is not there.

      ```python
      try:
          value = data['name']
      except KeyError:
          value = 'unknown'
      ```

      Catch only the exceptions you actually expect. A bare `except:` hides
      your own typos and turns a five second bug into an afternoon."""),

    C("what_is_a_module",
      ["what is a module", "how does import work in python",
       "explain importing in python"],
      """
      A module is just a .py file. Importing it runs that file once and gives
      you access to the names inside it.

      ```python
      import math
      from math import sqrt
      ```

      Python searches the current folder first, which is why naming your file
      `random.py` breaks `import random` - your file wins."""),

    C("what_is_pip",
      ["what is pip", "how do i install a python package",
       "explain pip"],
      """
      pip is Python's package installer. It downloads libraries from PyPI and
      puts them where your Python can import them.

      ```bash
      pip install requests
      pip install -r requirements.txt
      ```

      Install into a virtual environment rather than system-wide, so two
      projects can use different versions of the same library without
      fighting."""),

    C("what_is_a_virtual_environment",
      ["what is a virtual environment", "why do i need venv",
       "explain virtual environments"],
      """
      A virtual environment is a private folder of packages for one project,
      so installing something for project A cannot break project B.

      ```bash
      python -m venv .venv
      .venv\\Scripts\\activate      # Windows
      source .venv/bin/activate    # Mac and Linux
      ```

      Once it is active, `pip install` puts things inside that folder and
      nowhere else."""),

    C("f_string",
      ["what is an f string", "how do i format strings in python",
       "explain f strings"],
      """
      An f-string lets you put a variable or an expression straight inside a
      string by prefixing it with f.

      ```python
      name = 'Ada'
      print(f'Hello {name}, next year you are {age + 1}')
      ```

      You can format inside the braces too: `f'{value:.2f}'` gives two decimal
      places, and `f'{value=}'` prints the name and the value together, which
      is excellent for debugging."""),

    C("slicing",
      ["what is slicing in python", "explain list slicing", "how does [::-1] work"],
      """
      Slicing takes a section of a sequence with `[start:stop:step]`. Any of
      the three can be left out.

      ```python
      items[1:4]     # items 1, 2, 3 - stop is not included
      items[:3]      # the first three
      items[-1]      # the last one
      items[::-1]    # the whole thing, backwards
      ```

      A slice always returns a new object, so it never modifies the
      original."""),

    C("truthy_falsy",
      ["what is truthy and falsy in python", "what counts as false in an if statement",
       "explain truthiness"],
      """
      Python treats several values as False in a condition even though they
      are not the boolean False: 0, empty string, empty list, empty dict,
      empty tuple, and None.

      ```python
      if items:          # instead of if len(items) > 0
          ...
      ```

      That is why the idiomatic emptiness check is just the value itself."""),

    C("what_is_an_api",
      ["what is an api", "explain rest apis",
       "how do apis work"],
      """
      An API is a way for one program to ask another program for something,
      usually over HTTP.

      ```python
      import requests
      data = requests.get('https://api.example.com/users').json()
      ```

      You send a request to a URL, you get structured data back - normally
      JSON. The other side decides what it will let you ask for; that contract
      is the API."""),

    C("what_is_json",
      ["what is json", "explain json format",
       "how do i work with json"],
      """
      JSON is a text format for structured data. It looks almost exactly like
      Python dicts and lists, which is why it is so easy to work with here.

      ```python
      import json
      text = json.dumps({'name': 'Ada'})   # object -> string
      data = json.loads(text)              # string -> object
      ```

      The `s` in dumps and loads means string. Without the s, they read from
      and write to a file instead."""),

    C("what_is_git",
      ["what is git", "why should i use version control",
       "explain git"],
      """
      Git records snapshots of your project so you can see what changed, go
      back to any earlier state, and work on a feature without breaking the
      main version.

      ```bash
      git add .
      git commit -m "add login page"
      git push
      ```

      The habit that matters most: commit small and often, with a message
      that says why, not what."""),

    C("what_is_recursion",
      ["what is recursion", "explain recursive functions",
       "how does recursion work"],
      """
      Recursion is a function calling itself on a smaller version of the same
      problem, until the problem is small enough to answer directly.

      ```python
      def countdown(n):
          if n == 0:
              return
          print(n)
          countdown(n - 1)
      ```

      Every recursive function needs a base case that does not recurse.
      Without one, Python stops you with RecursionError at about a thousand
      levels deep."""),

    C("time_complexity",
      ["what is big o notation", "what does o(n) mean", "explain time complexity"],
      """
      Big O describes how the work grows as the input grows, ignoring
      constants.

      - O(1) - same cost no matter the size, like a dict lookup
      - O(n) - one pass, like summing a list
      - O(n log n) - a good sort
      - O(n^2) - a loop inside a loop, like bubble sort

      The point is not the exact number of steps. It is that an O(n^2)
      solution is fine for 100 items and hopeless for a million."""),

    C("what_is_an_algorithm",
      ["what is an algorithm", "explain what an algorithm is",
       "what makes something an algorithm"],
      """
      An algorithm is a finite list of unambiguous steps that turns an input
      into an output. A recipe, but with no room for interpretation.

      Binary search is an algorithm: halve the range, check the middle,
      repeat. What makes it worth naming is that it always works and you can
      state exactly how long it takes."""),

    C("debugging",
      ["how do i debug my python code", "my code is not working what do i do",
       "how do i find a bug"],
      """
      Read the traceback from the bottom up. The last line names the error,
      and the line above it points at the file and line number where it
      happened.

      Then narrow it down:

      ```python
      print(f'{value=} {type(value)=}')
      ```

      Print the values just before the crash. Most bugs are a variable that is
      not holding what you assumed it was holding."""),

    C("what_is_a_variable",
      ["what is a variable", "explain variables in python",
       "how do variables work"],
      """
      A variable is a name pointing at a value. In Python the name has no
      type - the value does - so you can point the same name at anything.

      ```python
      count = 5
      count = 'five'      # legal, though usually a bad idea
      ```

      Assignment never copies. `b = a` gives you a second name for the same
      list, so changing b changes what a sees too."""),

    C("indentation",
      ["why does python care about indentation", "what is an indentation error",
       "explain indentation in python"],
      """
      Indentation is how Python knows which lines belong to a block. Other
      languages use braces; Python uses the whitespace itself.

      ```python
      if ready:
          go()        # inside the if
      go()            # always runs
      ```

      Use four spaces and never mix tabs with spaces in the same file -
      that is the usual cause of `TabError` and `IndentationError`."""),

    C("comments",
      ["how do i write comments in python", "what is a docstring",
       "explain comments and docstrings"],
      """
      A comment starts with # and is ignored when the code runs. A docstring
      is a string on the first line of a function, and it stays available at
      runtime through help().

      ```python
      def area(w, h):
          \"\"\"Return the area of a rectangle.\"\"\"
          return w * h    # width times height
      ```

      Write comments about why, not what. The code already says what."""),

    C("what_is_an_llm",
      ["what is a large language model", "how does an llm work", "what is an llm"],
      """
      A large language model is a neural network trained on an enormous amount
      of text to do one thing: predict the next token.

      Everything else - answering questions, writing code, translating - comes
      out of doing that one job extremely well, plus a second training stage
      on examples of questions and answers. That second stage is called
      instruction tuning, and it is exactly what this session builds."""),

    C("what_is_a_token",
      ["what is a token", "how does tokenization work",
       "explain tokens"],
      """
      A token is the chunk of text a language model actually sees. It is
      usually a piece of a word rather than a whole one.

      "unbelievable" might arrive as `un` + `bel` + `iev` + `able`. Common
      words are one token, rare ones are several. That is why an API charges
      by token and not by word, and why models are bad at counting letters -
      they never see the letters."""),

    C("what_is_training",
      ["how is a model trained", "what does training a neural network mean",
       "explain model training"],
      """
      Training is a loop of five steps repeated thousands of times:

      1. take a batch of data
      2. let the model predict
      3. measure how wrong it was - the loss
      4. work out which direction each weight should move
      5. nudge every weight that way

      There is no step six. Everything else in machine learning is a detail
      hung off this loop."""),
]


ALL_TASKS = STRINGS + LISTS + NUMBERS + DICTS + FILES + PYTHON
ALL_CONCEPTS = CONCEPTS


if __name__ == "__main__":
    groups = [("strings", STRINGS), ("lists", LISTS), ("numbers", NUMBERS),
              ("dicts/sets", DICTS), ("files", FILES), ("python", PYTHON)]

    print("=" * 60)
    print("THE CURRICULUM - everything ARGPT-Coder will ever know")
    print("=" * 60)
    for label, group in groups:
        print(f"  {label:12s} {len(group):3d} tasks")
    print(f"  {'concepts':12s} {len(ALL_CONCEPTS):3d} questions")
    print("-" * 60)

    # how many DIFFERENT ways can each thing be asked?
    ways = sum(len(t["asks"]) * len(t["vars"]) for t in ALL_TASKS)
    print(f"  {len(ALL_TASKS)} coding tasks x phrasings x parameter names = {ways} variants")
    print(f"  {len(ALL_CONCEPTS)} concepts")
    print(f"  {len(BUGS)} kinds of bug to fix")
    print("\nbuild_data2.py multiplies this out into tens of thousands")
    print("of training examples, and tests every line of code first.")

# NOTE:
# - Want the model to know something new? Add one T(...) here and rebuild.
#   That is the entire workflow, and it is the same one the big labs use.
# - The {v} placeholder is not decoration. Without it the model memorises
#   `def is_even(n)` and gets confused the moment someone says `number`.
# - Every `test` is real. If you add a task with broken code, build_data2.py
#   refuses to build the dataset and tells you which one.
