from ..errorHandling          import ErrorHandlerCompiler, ErrorHandlerVariables
from ..factory               import Factory
import traceback

class InstructionRunner:
    def __init__(self, mem):
        self.__mem              = mem
        self.progDefs           = None
        self.current_line       = None # represents the current instruction
        self.stdout             = []
        self.printer            = []
        self.operators_executed_history    = []

    def run_line(self):
        last_history = self.operators_executed_history.copy()
        if self.getCurrentLine() >= self.__mem.num_instructions_saved():
            print("nothing more to run")
            return
        instruction = self.__mem.find_instruction(self.current_line)
        self.load_instruction()
        self.nextPosition()
        print("instruction: ", instruction)
        print("step", self.__mem.getSteps())
        print("\n____________\n")
        if instruction[0] in self.progDefs.possible_operators:
            return True
        else:
            return False

    def run_all(self):
        self.setStartPosition()
        self.run_saved_instructions()
    
    def setStartPosition(self):
        self.current_line = self.__mem.getMemoryBeforeCompile()

    def run_saved_instructions(self):
        try:
            while self.getCurrentLine() < self.__mem.num_instructions_saved():
                self.load_instruction()
                self.nextPosition()
        except Exception as err:
            print(traceback.format_exc())
            print("Hubo un error en runtime ", err.args, self.getCurrentLine(), err)

    def getCurrentLine(self):
        return self.current_line

    def load_instruction(self):
        instruction = self.__mem.find_instruction(self.getCurrentLine())
        operator = self.program_name(instruction)
        if operator in self.progDefs.get_possible_operators():
            self.run_operator(operator, instruction)
            self.save_in_history(instruction)

    def program_name(self, instruction):
        return instruction[0]

    def nextPosition(self):
        self.current_line += 1

    def run_operator(self, name, instruction):
        try:
            self.progDefs.get_possible_operators()[name](*instruction[1:])
        except TypeError:
            ErrorHandlerCompiler.throw_too_many_arguments(name, instruction)
            raise

    def save_in_history(self, instruction):
        self.operators_executed_history.append((self.current_line+1, instruction))

    def setLine(self, value):
        self.current_line = value

    def appendStdout(self, string):
        self.stdout.append(string)
    
    def appendPrinter(self, string):
        self.printer.append(string)

    def getPrinter(self):
        return self.printer

    def getStdout(self):
        return self.stdout

    def get_operators_executed_history(self):
        return self.operators_executed_history

    def num_prog_ran(self):
        return len(self.operators_executed_history)

    def setProgdefs(self, progDefs):
        self.progDefs = progDefs