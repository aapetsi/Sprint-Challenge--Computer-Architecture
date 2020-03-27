"""CPU functionality."""

import sys

HLT = 0b00000001
PRN = 0b01000111
LDI = 0b10000010
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
ST = 0b10000100


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.inc_size = 0
        # The MAR contains the address that is being read or written to.
        self.mar = 0
        # The MDR contains the data that was read or the data to write
        self.mdr = 0
        # BRANCH TABLE
        self.running = True
        self.branchtable = {}
        self.branchtable[LDI] = self.handle_ldi
        self.branchtable[HLT] = self.handle_hlt
        self.branchtable[PRN] = self.handle_prn
        self.branchtable[MUL] = self.handle_mul
        self.branchtable[PUSH] = self.handle_push
        self.branchtable[POP] = self.handle_pop
        # STACK POINTER
        self.sp = 7  # IT POINTS TO REGISTER NUMBER 7, WHICH ACCORDING TO
        # SPECS HOLDS THE STACK POINTER
        # WE SET THE INITIAL STACK POINTER TO 0XF3, THE MEMORY SLOT WHICH,
        # ACCORDING TO SPEC, IS THE START OF THE SPEC
        self.reg[self.sp] = 0xF4
        # CALL / RET
        self.branchtable[CALL] = self.handle_call
        self.branchtable[RET] = self.handle_ret
        self.branchtable[ADD] = self.handle_add
        # INTERRUPTS
        self.branchtable[ST] = self.handle_st

    def ram_read(self, address):
        value_in_memory = self.ram[address]
        # SETS MAR TO THE ADDRESS BEING READ
        self.set_mar(address)
        # SETS MDR TO THE VALUE STORED IN MEMORY
        self.set_mdr(value_in_memory)
        return value_in_memory

    def ram_write(self, address, value):
        self.ram[address] = value
        # SETS MAR TO THE ADDRESS BEING WRITTEN
        self.set_mar(address)
        # SETS MDR TO THE VALUE BEING WRITTEN
        self.set_mdr(value)
        return self.ram[address]

    def set_mar(self, address):
        self.mar = address

    def set_mdr(self, value):
        self.mdr = value

    def load(self):
        """Load a program into memory."""

        # address = 0

        # # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1
        """Load instructions from a file"""
        starting_memory = 0
        # debug = 1
        file_name = sys.argv[1]
        with open(file_name) as f:
            for line in f:
                # WE DIVIDE LINE IF THERE IS A COMMENT
                comment_split = line.split('#')
                # WE TAKE THE LEFT PART OF THE ARRAY, AND STRIP SPACE AT THE
                # END
                instruction = comment_split[0].strip()
                # print(f'Instruction: {instruction} in line {debug}')
                if instruction == '':
                    continue
                # WE CONVERT STRING WITH BINARY CODE INTO BINARY VALUE
                binary_code = int(instruction, 2)
                # WE SAVE EACH INSTRUCTION INTO RAM
                self.ram_write(starting_memory, binary_code)
                # WE INCREMENT THE ADDRESS IN MEMORE SO WE CAN ADD THE NEXT
                # INSTRUCTION IN THE NEXT SLOT
                starting_memory += 1
                # debug += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        # MUL
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def handle_ldi(self, IR, operand_a, operand_b):
        # print("#### LDI START ####")
        # self.trace()
        # self.print_stack()
        # print("-------------------")
        self.reg[operand_a] = operand_b
        self.inc_size = 3
        # self.trace()
        # self.print_stack()
        # print("---- LDI END ----")

    def handle_prn(self, IR, operand_a, operand_b):
        value = self.reg[operand_a]
        self.inc_size = 2
        print(value)

    def handle_mul(self, IR, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)
        self.inc_size = 3

    def handle_hlt(self, IR, operand_a, operand_b):
        print("Operations halted.")
        sys.exit(-1)
        self.running = False

    # HELPER FUNCTION TO DEBUG
    # def print_stack(self):
    #     for i in range(0xF4, self.stack_pointer - 1, -1):
    #         print(f'Position in ram: {hex(i)}. Value: {self.ram[i]}')

    def handle_push(self, IR, operand_a=None, operand_b=None):
        # print("#### PUSH START ####")
        # self.trace()
        # self.print_stack()
        # print("-------------------")
        if IR == CALL:
            value = operand_a
        else:
            # WE GRAB THE VALUE AT THE REGISTER WE WANT TO PUSH
            value = self.reg[operand_a]
        # WE DECREASE THE STACK POINTER BY ONE, SINCE WE ARE ADDING AN ITEM
        # INTO THE STACK AND THE HEAD IS NOW ONE SLOT DOWN
        self.reg[self.sp] -= 1
        # WE SET THE HEAD OF THE STACK TO THE VALUE EXTRACTED FROM THE REGISTER
        # self.ram[self.reg[self.sp]] = value
        self.ram_write(self.reg[self.sp], value)
        # WE SET THE SIZE FOR PC FOR NEXT INSTRUCTION TO TAKE PLACE
        self.inc_size = 2
        # self.trace()
        # self.print_stack()
        # print("---- PUSH END ----")

    def handle_pop(self, IR, operand_a=None, operand_b=None):
        # print("### POP START ###")
        # self.trace()
        # self.print_stack()
        # print("-------------------")

        # WE EXTRACT THE VALUE AT THE HEAD OF THE STACK
        value = self.ram[self.reg[self.sp]]
        if operand_a:
            # WE SET THE VALUE OF THE REGISTER TO THE VALUE EXTRACTED FROM THE
            # HEAD OF THE STACK
            self.reg[operand_a] = value
            # WE DECREASE THE HEAD OF THE STACK SINCE WE REMOVED AN ELEMENT
            # FROM IT
            self.reg[self.sp] += 1
            # WE SET THE SIZE FOR PC FOR NEXT INSTRUCTION TO TAKE PLACE
            self.inc_size = 2
            # self.trace()
            # self.print_stack()
            # print("---- POP END ----")
        else:
            return value

    def handle_call(self, IR, operand_a, operand_b):
        # address in memory where instruction after call self.pc will be set so
        # CPU execution continues
        next_instruction = self.pc + 2
        # CALL ONLY USES ONE OPERAND. THEREFORE, OPERAND B IS THE NEXT
        # INSTRUCTION AFTER CALL IS RETURNED
        self.handle_push(IR, next_instruction)
        # set program counter to the value in the register being passed with
        # call
        self.pc = self.reg[operand_a]

    def handle_ret(self, IR, operand_a, operand_b):
        # we set self.pc to the value extracted from the head of the stack
        value = self.handle_pop(IR)
        self.pc = value

    def handle_add(self, IR, operand_a, operand_b):
        self.alu("ADD", operand_a, operand_b)
        self.inc_size = 3

    def handle_st(self, IR, operand_a, operand_b):
        value = self.reg[operand_b]
        self.ram_write(self.reg[operand_a], value)
        self.inc_size = 3

    def run(self):
        """Run the CPU."""
        # running = True
        instructions_set_pc = [CALL, RET]

        while self.running:
            # INSTRUCTION REGISTER
            IR = self.ram_read(self.pc)
            # print(self.pc, "<<<<<< PC")
            # GET THE NEXT 2 BYTES OF DATA IN CASE WE NEED THEM
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # """ CODE AFTER BRANCH TABLE """
            if self.branchtable.get(IR):
                self.branchtable[IR](IR, operand_a, operand_b)
                # for instructions that set PC themselves: i.e. CALL, RET
                if IR not in instructions_set_pc:
                    # self.branchtable[IR](IR, operand_a, operand_b)
                    self.pc += self.inc_size

            # """ CODE BEFORE BRANCH TABLE """
            # LDI
            # if IR == LDI:
                #     self.reg[operand_a] = operand_b
                #     inc_size = 3
            # PRN
            # elif IR == PRN:
                # value = self.reg[operand_a]
                # print(value)
                # self.inc_size = 2
            # MUL
            # elif IR == MUL:
                # self.alu("MUL", operand_a, operand_b)
                # self.inc_size = 3
            # HLT
            # elif IR == HLT:
            #     print("Operations halted.")
            #     sys.exit(-1)
            #     running = False
            # INSTRUCTION NOT RECOGNISED

            else:
                print("Invalid instruction")
                self.running = False

#     def run(self):
#         """Run the CPU."""
#         HLT = 1
#         PRN = 71
#         LDI = 130
#         MUL = 162
#         PUSH = 69
#         POP = 70
#         CALL = 80
#         RET = 17

#         inc = 0

#         while not self.halt:

#             command = self.ram_read(self.pc)
#             operand_a = self.ram_read(self.pc + 1)
#             operand_b = self.ram_read(self.pc + 2)

#             if command == HLT:
#                 self.halt = True
#                 sys.exit(-1)

#             elif command == PRN:
#                 register_index = operand_a
#                 num = self.registers[register_index]
#                 print(num)
#                 inc = 2

#             elif command == LDI:
#                 self.registers[operand_a] = operand_b
#                 inc = 3

#             elif command == MUL:
#                 self.alu('MUL', operand_a, operand_b)
#                 inc = 3

#             elif command == PUSH:
#                 val = self.registers[operand_a]
#                 self.registers[SP] -= 1
#                 self.ram_write(self.registers[SP],val)
#                 inc = 2

#             elif command == POP:
#                 val = self.ram_read(self.registers[SP])
#                 self.registers[SP] += 1
#                 self.registers[operand_a] = val
#                 inc = 2

#             else:
#                 print("Invalid instruction")
#                 self.halt = False

#             self.pc += inc

#     def ram_read(self, address):
#         return self.ram[address]

#     def ram_write(self, address, value):
#         self.registers[address] = value
#         return self.ram[address]