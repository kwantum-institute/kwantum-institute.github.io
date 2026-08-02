import Article from "../Article";

function PythonVsJava() {
  return (
    <Article
      title="Technical Documentation - Java vs Python"
      content={
        <>
          <header className="header">Java vs Python Documentation</header>
          <main className="main-doc" id="main-doc">
            <section className="main-section" id="Hello,_World!">
              <header className="section-header">Hello, World!</header>
              <p>
                The "Hello, World!" program is often the first program written
                when learning a new language. In Java, this involves creating a
                class and defining the main method, where you use
                `System.out.println` to print the string to the console. The
                syntax requires the use of curly braces and semicolons, which
                makes the structure more formal and verbose.
              </p>
              <code className="code">
                public class Main &#123;
                <br /> &nbsp;&nbsp;public static void main(String[] args) &#123;
                <br /> &nbsp;&nbsp;&nbsp;&nbsp;System.out.println("Hello,
                World!");
                <br /> &nbsp;&nbsp;&#125;
                <br />
                &#125;
              </code>
              <p>
                In contrast, Python simplifies this process significantly. You
                can print "Hello, World!" with a single line of code using the
                `print` function. This simplicity and ease of use make Python
                more approachable for beginners.
              </p>
              <code className="code">print("Hello, World!")</code>
            </section>

            <section className="main-section" id="Variables">
              <header className="section-header">Variables</header>
              <p>
                Variables in programming are used to store data values. Java is
                a statically typed language, meaning that you must declare the
                type of variable before using it. For example, to store the
                number 5, you would write `int number = 5;`. This explicit
                declaration helps catch errors at compile time and can make the
                code more predictable.
              </p>
              <code className="code">int number = 5;</code>
              <p>
                Python, on the other hand, is dynamically typed, so you do not
                need to declare the type of a variable explicitly. You can
                simply write `number = 5`, and Python will infer that it is an
                integer. This flexibility makes Python faster to write and
                easier to read, although it can sometimes lead to runtime errors
                that would be caught at compile time in Java.
              </p>
              <code className="code">number = 5</code>
            </section>

            <section className="main-section" id="Data_Types">
              <header className="section-header">Data Types</header>
              <p>
                Both Java and Python support a variety of data types, though
                they handle them differently. In Java, data types are divided
                into primitive types (such as int, float, double, boolean, char)
                and objects. Primitive types are not objects and are therefore
                more efficient in terms of memory usage and performance.
                Examples of Java primitive types include:
              </p>
              <ul>
                <li>int</li>
                <li>float</li>
                <li>double</li>
                <li>boolean</li>
                <li>char</li>
              </ul>
              <p>
                In Python, however, everything is treated as an object. This
                includes basic data types such as int, float, bool, and str, as
                well as more complex types like lists, tuples, and dictionaries.
                This object-oriented nature of Python provides greater
                flexibility and powerful built-in methods for data manipulation,
                although it may come at the cost of some performance compared to
                Java's primitive types.
              </p>
              <code className="code">
                int, float, bool, str, list, tuple, dict, etc.
              </code>
            </section>

            <section className="main-section" id="If-Else_Statements">
              <header className="section-header">If-Else Statements</header>
              <p>
                Conditional statements allow a program to execute different code
                paths based on certain conditions. In Java, an if-else statement
                is enclosed in curly braces, and each condition must be followed
                by parentheses and a semicolon. For example, to check if a
                number is positive, you would write `if (x &gt; 0) &#123;
                System.out.println("Positive"); &#125; else &#123;
                System.out.println("Negative"); &#125;`. This structure is clear
                but requires more syntax elements.
              </p>
              <code className="code">
                if (x &gt; 0) &#123;
                <br /> &nbsp;&nbsp;System.out.println("Positive");
                <br />
                &#125; else &#123;
                <br /> &nbsp;&nbsp;System.out.println("Negative");
                <br />
                &#125;
              </code>
              <p>
                In Python, if-else statements rely on indentation to define the
                scope of each condition, which results in a more streamlined and
                readable syntax. You can check if a number is positive with the
                following code: `if x &gt; 0: print("Positive") else:
                print("Negative")`. This indentation-based approach reduces the
                need for additional characters and makes the code easier to read
                at a glance.
              </p>
              <code className="code">
                if x &gt; 0:
                <br /> &nbsp;&nbsp;print("Positive")
                <br />
                else:
                <br /> &nbsp;&nbsp;print("Negative")
              </code>
            </section>

            <section className="main-section" id="Loops">
              <header className="section-header">Loops</header>
              <p>
                Loops are fundamental in programming for iterating over a
                sequence of elements or executing a block of code multiple
                times. Java's for loop is more verbose, requiring explicit
                initialization, condition, and increment expressions within
                parentheses, followed by a block of code in curly braces. For
                example, `for (int i = 0; i &lt; 5; i++) &#123;
                System.out.println(i); &#125;` iterates from 0 to 4, printing
                each value.
              </p>
              <code className="code">
                for (int i = 0; i &lt; 5; i++) &#123;
                <br /> &nbsp;&nbsp;System.out.println(i);
                <br />
                &#125;
              </code>
              <p>
                Python's for loop is more concise and intuitive, using the
                `range` function to generate a sequence of numbers. The
                equivalent loop in Python would be `for i in range(5):
                print(i)`, which achieves the same result with fewer lines of
                code and no need for explicit initialization or incrementing.
              </p>
              <code className="code">
                for i in range(5):
                <br /> &nbsp;&nbsp;print(i)
              </code>
              <p>
                When it comes to while loops, Java again requires more syntax. A
                Java while loop, such as `int i = 0; while (i &lt; 5) &#123;
                System.out.println(i); i++; &#125;`, uses explicit condition
                checking and incrementing within the loop body. Python's while
                loop simplifies this to `i = 0 while i &lt; 5: print(i) i += 1`,
                maintaining readability and reducing the syntactic overhead.
              </p>
              <code className="code">
                int i = 0;
                <br />
                while (i &lt; 5) &#123;
                <br /> &nbsp;&nbsp;System.out.println(i);
                <br /> &nbsp;&nbsp;i++;
                <br />
                &#125;
              </code>
              <code className="code">
                i = 0<br />
                while i &lt; 5:
                <br /> &nbsp;&nbsp;print(i)
                <br /> &nbsp;&nbsp;i += 1
              </code>
            </section>

            <section className="main-section" id="Classes">
              <header className="section-header">Classes</header>
              <p>
                Both Java and Python support object-oriented programming through
                the use of classes. In Java, a class definition includes access
                modifiers (such as public or private), methods, and member
                variables. For example, a simple class definition might look
                like `public class Dog &#123; String breed; public void bark()
                &#123; System.out.println("Woof"); &#125; &#125;`. This
                structure enforces encapsulation and helps manage access to the
                class's methods and properties.
              </p>
              <code className="code">
                public class Dog &#123;
                <br /> &nbsp;&nbsp;String breed;
                <br /> &nbsp;&nbsp;public void bark() &#123;
                <br /> &nbsp;&nbsp;&nbsp;&nbsp;System.out.println("Woof");
                <br /> &nbsp;&nbsp;&#125;
                <br />
                &#125;
              </code>
              <p>
                In Python, classes are defined with the `class` keyword, and
                methods are defined with the `def` keyword. Python does not
                require explicit access modifiers, and indentation is used to
                define the scope of the class and its methods. For example, a
                similar class in Python would be `class Dog: def __init__(self,
                breed): self.breed = breed def bark(self): print("Woof")`. This
                approach is more concise and easier to read, although it may
                lack the strict access controls provided by Java.
              </p>
              <code className="code">
                class Dog:
                <br /> &nbsp;&nbsp;def __init__(self, breed):
                <br /> &nbsp;&nbsp;&nbsp;&nbsp;self.breed = breed
                <br /> &nbsp;&nbsp;def bark(self):
                <br /> &nbsp;&nbsp;&nbsp;&nbsp;print("Woof")
              </code>
            </section>

            <section className="main-section" id="Arrays">
              <header className="section-header">Arrays</header>
              <p>
                Arrays are fundamental data structures used to store collections
                of elements. In Java, arrays are declared with a specific size
                and type, such as `int[] numbers = new int[5];`. Once declared,
                elements can be accessed and modified using their indices, as in
                `numbers[0] = 1;`. This fixed-size nature of Java arrays can be
                limiting but also ensures memory efficiency.
              </p>
              <code className="code">
                int[] numbers = new int[5];
                <br />
                numbers[0] = 1;
              </code>
              <p>
                Python provides more flexibility with lists, which can
                dynamically grow or shrink in size. A list is created using
                square brackets, and elements can be added, removed, or accessed
                using built-in methods. For example, `numbers = [1, 2, 3, 4, 5]`
                creates a list, and `numbers.append(6)` adds a new element to
                it. This dynamic nature makes Python lists more versatile for
                various programming tasks.
              </p>
              <code className="code">
                numbers = [1, 2, 3, 4, 5]
                <br />
                numbers.append(6)
              </code>
            </section>

            <section className="main-section" id="Algorithms">
              <header className="section-header">Algorithms</header>
              <p>
                Implementing algorithms in Java and Python involves similar
                logic, but the syntax and built-in functions differ. For
                example, to find the maximum value in an array, Java requires a
                loop to iterate through the elements and compare each one. The
                following code demonstrates this process: `int max = arr[0]; for
                (int i = 1; i &lt; arr.length; i++) &#123; if (arr[i] &gt; max)
                &#123; max = arr[i]; &#125; &#125;`. This approach is explicit
                and requires managing loop variables and conditions.
              </p>
              <code className="code">
                int max = arr[0];
                <br />
                for (int i = 1; i &lt; arr.length; i++) &#123;
                <br /> &nbsp;&nbsp;if (arr[i] &gt; max) &#123;
                <br /> &nbsp;&nbsp;&nbsp;&nbsp;max = arr[i];
                <br /> &nbsp;&nbsp;&#125;
                <br />
                &#125;
              </code>
              <p>
                In Python, built-in functions like `max` simplify this task. You
                can find the maximum value in a list with a single line of code:
                `max_value = max(arr)`. This built-in functionality enhances
                readability and reduces the amount of code needed to achieve the
                same result, making Python a more convenient choice for many
                algorithmic tasks.
              </p>
              <code className="code">max_value = max(arr)</code>
            </section>

            <section className="main-section" id="Inheritance">
              <header className="section-header">Inheritance</header>
              <p>
                Inheritance is a core principle of object-oriented programming,
                allowing classes to inherit properties and methods from a parent
                class. In Java, inheritance is achieved using the `extends`
                keyword. For example, a subclass `Labrador` that extends the
                `Dog` class would be defined as `public class Labrador extends
                Dog &#123; &#125;`. This approach enforces strict type
                hierarchies and helps maintain code organization.
              </p>
              <code className="code">
                public class Labrador extends Dog &#123;
                <br />
                &#125;
              </code>
              <p>
                Python uses a more straightforward syntax for inheritance, with
                the parent class listed in parentheses after the subclass name.
                For example, `class Labrador(Dog): pass` defines a subclass
                `Labrador` that inherits from the `Dog` class. This simplicity
                makes inheritance easy to implement and understand, although it
                may lack some of the explicit type safety features found in
                Java.
              </p>
              <code className="code">
                class Labrador(Dog):
                <br /> &nbsp;&nbsp;pass
              </code>
            </section>

            <section className="main-section" id="Recursion">
              <header className="section-header">Recursion</header>
              <p>
                Recursion involves a function calling itself to solve a problem
                in smaller subproblems. In Java, recursion requires defining the
                base case and recursive case explicitly, as in the following
                example to calculate the factorial of a number: `public int
                factorial(int n) &#123; if (n &lt;= 1) &#123; return 1; &#125;
                else &#123; return n * factorial(n - 1); &#125; &#125;`. This
                clear separation of cases helps manage the flow of recursive
                calls.
              </p>
              <code className="code">
                public int factorial(int n) &#123;
                <br /> &nbsp;&nbsp;if (n &lt;= 1) &#123;
                <br /> &nbsp;&nbsp;&nbsp;&nbsp;return 1;
                <br /> &nbsp;&nbsp;&#125; else &#123;
                <br /> &nbsp;&nbsp;&nbsp;&nbsp;return n * factorial(n - 1);
                <br /> &nbsp;&nbsp;&#125;
                <br />
                &#125;
              </code>
              <p>
                In Python, recursion follows a similar structure but with less
                syntax. The same factorial function can be written as `def
                factorial(n): if n &lt;= 1: return 1 else: return n *
                factorial(n - 1)`. Python's clean and concise syntax makes
                recursive functions easy to write and understand, enhancing code
                readability and maintainability.
              </p>
              <code className="code">
                def factorial(n):
                <br /> &nbsp;&nbsp;if n &lt;= 1:
                <br /> &nbsp;&nbsp;&nbsp;&nbsp;return 1<br /> &nbsp;&nbsp;else:
                <br /> &nbsp;&nbsp;&nbsp;&nbsp;return n * factorial(n - 1)
              </code>
            </section>
          </main>
        </>
      }
    />
  );
}

export default PythonVsJava;
