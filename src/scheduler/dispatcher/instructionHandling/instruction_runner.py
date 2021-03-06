from ..errorHandling  import ErrorHandlerCompiler, ErrorHandlerVariables
import traceback

class InstructionRunner:
    def __init__(self, mem):
        self.__mem         = mem
        self.dataStream    = mem.getDataStream()
        self.progDefs      = None
        self.current_line  = None # represents the current instruction
        self.operators_executed_history    = []

    def getMemory(self):
        return self.__mem

    def run_line(self):
        self.startCurrentLineAt0IfNone()
        runnable = self.possibleToRun()
        self.run_saved_instructionsEx(num_lines_to_run=1)
        return runnable

    def possibleToRun(self):
        program = [self.__mem.getInstructionFromDeclaration(self.progDefs.getDeclaration())]
        print(f"current line: {self.getCurrentLine()}")
        if self.getCurrentLine() > len(program[0]) - 1:
            return False
        instruction = self.find_instruction(program, self.getCurrentLine()) 
        operator = self.program_name(instruction)
        if operator in self.progDefs.get_possible_operators():
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
            queues = self.__mem.getQueues()
            programs_to_run = queues.getPendingPrograms()
            while self.getCurrentLine() < len(programs_to_run[0]):
                self.load_instruction(programs_to_run)
                self.nextPosition()
            programs_to_run.pop(0)
            self.__mem.saveDeclaration(self.progDefs.getDeclaration(), True)
        except Exception as err:
            print(traceback.format_exc())
            message = "Hubo un error en runtime ", "linea: ", self.getCurrentLine(), "instrucción: ", self.find_instruction(programs_to_run, self.getCurrentLine()), err
            ErrorHandlerVariables.try_error(self, self.dataStream, message)

    def getCurrentLine(self):
        return self.current_line

    def load_instruction(self, programs_to_run):
        instruction = self.find_instruction(programs_to_run, self.getCurrentLine()) 
        operator = self.program_name(instruction)
        # print(f"the instruction is: {instruction}")
        self.__mem.saveInstanceAsLastRun(self)
        if operator in self.progDefs.get_possible_operators():
            self.run_operator(operator, instruction)
            self.save_in_history(instruction)
        else: 
            if operator not in self.__mem.settings.getOperationsAndDeclarationsPossible():
                print("todas las funciones: ", self.__mem.settings.getOperationsAndDeclarationsPossible())
                message = "Hubo un error en runtime ", "linea: ", self.getCurrentLine(), "funcion no definida: ", operator
                ErrorHandlerVariables.funcion_no_definida(self, self.dataStream, message)

    def find_instruction(self, programs_to_run, id_):
        # print("in find instruction, id: ", id_)
        return programs_to_run[0][id_]

    def program_name(self, instruction):
        return instruction[0]

    def nextPosition(self):
        self.current_line += 1

    def run_operator(self, name, instruction):
        try:
            # print("the declaration is: ", self.progDefs.getDeclaration().getVariables())
            # print(f"the instruction is: {instruction} \n")
            self.progDefs.get_possible_operators()[name](*instruction[1:])
        except Exception:
            ErrorHandlerCompiler.throw_too_many_arguments(self, self.dataStream, name, instruction)
            raise

    def save_in_history(self, instruction):
        self.operators_executed_history.append((self.current_line+1, instruction))

    def setLine(self, value):
        self.current_line = value

    def run_all_expro(self,num_lines_to_run):
        self.startCurrentLineAt0IfNone()
        self.run_saved_instructionsEx(num_lines_to_run)

    def startCurrentLineAt0IfNone(self):
        if self.current_line == None:
            self.current_line = 0

    def run_saved_instructionsEx(self, num_lines_to_run):
        try:
            programs_to_run = [self.__mem.getInstructionFromDeclaration(self.progDefs.getDeclaration())]
            limit = self.getCurrentLine() + num_lines_to_run
            while self.getCurrentLine() < limit:
                if self.getCurrentLine() >= len(programs_to_run[0]):
                    programs_to_run.pop(0)
                    break
                self.load_instruction(programs_to_run)
                self.nextPosition()
            print("\n")
            self.__mem.saveDeclaration(self.progDefs.getDeclaration(), update=True)
        except Exception as err:
            print(traceback.format_exc())
            print("Hubo un error en runtime ", err.args, self.getCurrentLine(), err)

    def get_operators_executed_history(self):
        return self.operators_executed_history

    def run_line_expro(self):
        pass

    def num_prog_ran(self):
        return len(self.operators_executed_history)

    def setProgdefs(self, progDefs):
        self.progDefs = progDefs
        self.__mem.settings.appendDeclarationsPossible(self.progDefs.possible_operators)

    def getFilename(self):
        declaration = self.progDefs.getDeclaration()
        instruction = self.__mem.getInstructionFromDeclaration(declaration)
        index       = self.__mem.get_programs().index(instruction)
        fileInfo    = self.__mem.getFileInfo()
        return fileInfo.getFilenames()[index]