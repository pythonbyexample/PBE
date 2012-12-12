#!/usr/bin/env python3

import os, sys, shelve, random
from pprint import pprint

from utils import nl, range1

showRightAns = False     # print right answer if user got it wrong

qfname = "questions.db"
questions = []

def loadQuestions():
    qfp = shelve.open(qfname)
    for key in qfp.keys():
        for question in qfp[key]:
            questions.append((key, question))


def ask_text(question):
    """ Ask a question, return true or false.

        question looks like: (question, ((answer,0), (answer,1),) ...) where 1 means the right
        answer
        return question text and the number of the right answer & text string of right ans
    """
    random.shuffle(question[1])
    ans  = question[1]
    text = question[0] + nl

    for a in range(len(ans)):
        text += "%d) %s\n" % (a+1, ans[a][0])
        if ans[a][1] == 1:
            right = a + 1
            right_ans = ans[a][0]

    return text, right, right_ans


def ask(question):
    """ Ask a question, return true or false.

        question looks like: (question, ((answer,0), (answer,1),) ...) where 1 means the right
        answer

        returns isRight, right_ans # where isRight is 0 or 1, and right_ans is a string
    """
    random.shuffle(question[1])
    ans = question[1]

    while 1:
        print(question[0])
        right_ans = None

        for a in range(len(ans)):
            print("%d) %s" % (a+1,ans[a][0]))
            if ans[a][1]:
                right_ans = ans[a][0]

        answer = input("=====> ")
        if answer == 'q':
            sys.exit()

        try               : answer = int(answer)
        except ValueError : continue

        if answer > len(ans) or answer < 1:
            continue
        return ans[answer-1][1], right_ans


def testAskText():
    q = ["In low-level light conditions, the eyes of Tawny Owl are:",
        [["50 times better than human eyes.", 0],
        ["100 times better than human eyes.", 1],
        ["200 times better than human eyes.", 0],
        ["300 times better than human eyes.", 0],]]
    tmp = ask_text(q)
    assert tmp[2] == "100 times better than human eyes."

    print("Tests passed!")


def tests():
    testAskText()


def main():
    loadQuestions()
    pprint(questions[0])

    tests()

    q = random.choice(questions)[1]
    text, right, right_ans = ask_text(q)
    print(text)
    print("Right answer:", right_ans)
    print(nl*2)


    while 1:
        q = random.choice(questions)[1]
        result, right_ans = ask(q)
        if result:
            print "!!!Right answer!!!!"
            print
        else:
            print "...Wrong answer...",
            if showRightAns:
                print "(%s)" % right_ans
            else:
                print
            print

if __name__ == "__main__":
    main()
