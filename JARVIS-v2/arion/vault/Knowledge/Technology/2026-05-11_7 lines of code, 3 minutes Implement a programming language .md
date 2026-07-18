---
title: "7 lines of code, 3 minutes: Implement a programming language (2010)"
source: https://matt.might.net/articles/implementing-a-programming-language/
date: 2026-05-11
tags:
  - news
  - auto-learning
  - auto-injected
---

# 7 lines of code, 3 minutes: Implement a programming language (2010)

A small (yet Turing-equivalent) language
The easiest programming language to implement is a minimalist, higher-order functional programming language known as the lambda calculus.
The lambda calculus actually lives at the core of all the major functional languages--Haskell, Scheme and ML--but it also lives inside JavaScript, Python and Ruby. It's even hiding inside Java, if you know where to find it.
A brief history
Alonzo Church developed the lambda calculus in 1929.
Back then, it wasn't called a programming language because there were no computers; there wasn't anything to "program."
It was really just a mathematical notation for reasoning about functions.
Fortunately, Alonzo Church had a Ph.D. student named Alan Turing.
Alan Turing defined the Turing machine, which became the first accepted definition of a general-purpose computer.
It was soon discovered that the lambda calculus and the Turing machine were equivalent: any function you could describe with the lambda calculus could be implemented on a Turing machine, and any function you could implement on a Turing machine could be described in the lambda calculus.
What makes this remarkable is that there are only three kinds of expressions in the lambda calculus: variable references, anonymous functions and function calls.
Anonymous functions
Anonymous functions are written with a "lambda-dot" notation, so that:
(λ v . e)
is the function that accepts an argument v
and returns the value of e
.
If you've programmed in JavaScript, this form is equivalent to:
function (v) { return e ; }
Function call
Function call is written by making two expressions adjacent:
(f e)
In JavaScript (or just about any other language), you'd write this as:
f(e)
Examples
The identity function, which just returns its argument, is easy to write:
(λ x . x)
We can apply the identity function to the identity function:
((λ x . x) (λ a . a))
(Which of course just returns the identity function.)
Here's a (slightly) more interesting program:
(((λ f . (λ x . (f x))) (λ a . a)) (λ b . b))
Can you figure out what it does?
Wait! How the heck is this a "programming" language?
At first glance, this simple language seems to lack both recursion and iteration, not to mention numbers, booleans, conditionals, data structures and all the rest. How can this language possibly be general-purpose?
The way that the lambda calculus achieves Turing-equivalence is through two of the coolest programming hacks out there: Church encodings and the Y combinator.
I've written an entire article on the Y combinator and another one on Church encodings. But, if you don't want to read those, I can convince you that there's more to the lambda calculus than you probably expected with just one program:
((λ f . (f f)) (λ f . (f f)))
This outwardly benign program is called Omega, and if you try to execute it, it doesn't terminate! (See if you can figure out why.)
Implementing the lambda calculus
Below is the 7-line, 3-minute interpreter for the lambda calculus, in R5RS Scheme. In technical terms (explained below), it's an environment-based denotational interpreter.
; eval takes an expression and an environment to a value (define (eval e env) (cond ((symbol? e) (cadr (assq e env))) ((eq? (car e) 'λ) (cons e env)) (else (apply (eval (car e) env) (eval (cadr e) env))))) ; apply takes a function and an argument to a value (define (apply f x) (eval (cddr (car f)) (cons (list (cadr (car f)) x) (cdr f)))) ; read and parse stdin, then evaluate: (display (eval (read) '())) (newline)
This code will read a program from stdin, parse it, evaluate it and print the result. (It's 7 lines without the comments and blank lines.)
Scheme's read
function makes lexing and parsing
simple--as long as you're willing to live in the
"balanced parentheses" (i.e. s-expression) world of syntax. (If not, you'll have to read
up on lexing in parsing; you can start with one
of my articles on lexing.)
In Scheme, read
grabs properly parenthesized input from
stdin and parses it into a tree.
Two functions form the core of the interpreter:
eval
and apply
.
Even though we're in Scheme, we can give conceptual "signatures" to these functions:
eval : Expression * Environment -> Value apply : Value * Value -> Value Environment = Variable -> Value Value = Closure Closure = Lambda * Environment
The eval
function takes an expression and an enviroment to a value.
The expression can be either a variable, a lambda term or an application.
An environment is a map from variables to values, used to define the free variables of an open term.
(An open term is one that has unbound occurrences of a variable.)
Consider, for example, the expression (λ x . z)
.
This term is open, because we don't know what z
is.
Since we're in R5RS Scheme, we can use associative lists to define environments.
A closure is an encoding of a function that pairs a (possibly open) lambda expression with an environment to define its free variables. In other words, a closure closes an open term.
A cleaner imple

---
*Synthesized by AutonomousLearner*
