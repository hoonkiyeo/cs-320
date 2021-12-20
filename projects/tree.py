# project: p2
# submitter: yeo9
# partner: none
# hours: 25hrs




from zipfile import ZipFile, ZIP_DEFLATED
from io import TextIOWrapper
import json
import csv

#ZippedCSVReader class
class ZippedCSVReader:
    def __init__(self, filename):
        self.zipfile = filename
        self.paths = []
        with ZipFile(filename) as zf:
            for info in zf.infolist(): 
                self.paths.append(info.filename)
        sorted(self.paths) #sorted in alphabetical order

    
    def rows(self, filename = None):
   
        with ZipFile(self.zipfile) as zf:
            if not filename == None:
                with zf.open(filename) as f:
                    tio = TextIOWrapper(f)
                    reader = csv.DictReader(tio)
                    for row in reader:
                        yield row
             
            else: #read all csv files
                for filename in self.paths:
                    with zf.open(filename) as f:
                        tio = TextIOWrapper(f)
                        reader = csv.DictReader(tio)
                        for row in reader:
                            yield row

#Loan class
class Loan:
    def __init__(self, amount, purpose, race, sex, income, decision):
        self.amount = amount
        self.purpose = purpose
        self.race = race
        self.sex = sex
        self.income = income
        self.decision = decision
        
        
    def __repr__(self):
         return f"Loan({self.amount}, {repr(self.purpose)}, {repr(self.race)}, {repr(self.sex)}, {self.income}, {repr(self.decision)})"
         

    def __getitem__(self, lookup):
        if lookup == "amount":
            return self.amount
        elif lookup == "purpose":
            return self.purpose
        elif lookup == "race":
            return self.race
        elif lookup == "sex":
            return self.sex
        elif lookup == "income":
            return self.income
        elif lookup == "decision":
            return self.decision
        elif lookup == self.amount or lookup == self.purpose or lookup == self.race or lookup == self.sex or lookup == self.income or lookup == self.decision:
            return 1
        else:
            return 0 
        
        
        
        
#Bank class        
class Bank:
    def __init__(self, name, reader):
        self.name = name
        self.reader = reader
    def loans(self):
        dict_rows = self.reader.rows()
        for row in dict_rows:
            if not self.name or row['agency_abbr'] == self.name:
                amount = int(row['loan_amount_000s']) if row['loan_amount_000s'] != "" else 0
                purpose = row['loan_purpose_name'] if row['loan_purpose_name'] != "" else 0
                race = row['applicant_race_name_1'] if row['applicant_race_name_1'] != "" else 0
                sex = row['applicant_sex_name'] if row['applicant_sex_name'] != "" else 0
                income = int(row['applicant_income_000s']) if row['applicant_income_000s'] != "" else 0
                decision = "approve" if row['action_taken'] == 1 else "deny"
                new_loan = Loan(amount,purpose,race,sex,income,decision)
                yield new_loan
                
def get_bank_names(reader):
    bank_list = []
    rows = reader.rows()
    for row in rows:
        bank = row['agency_abbr']
        if bank not in bank_list:
            bank_list.append(bank)
            
    return sorted(bank_list)

#SimplePredictor Class
class SimplePredictor():
    def __init__(self):
        self.approved = 0
        self.denied = 0
        
    def predict(self, loan):
        if loan["purpose"] == "Refinancing":
            self.approved += 1
            return True
        else:
            self.denied += 1
            return False

    def get_approved(self):
        return self.approved

    def get_denied(self):
        return self.denied
    
#Node Class
class Node(SimplePredictor):
    def __init__(self, field, threshold, left, right):
        super().__init__()
        self.field = field
        self.threshold = threshold
        self.left = left
        self.right = right
        
    def dump(self, indent=0):
        if self.field == "class":
            line = "class=" + str(self.threshold)
        else:
            line = self.field + " <= " + str(self.threshold)
        print("  "*indent+line)
        if self.left != None:
            self.left.dump(indent+1)
        if self.right != None:
            self.right.dump(indent+1)
    
    def node_count(self):
        if self.left == None and self.right == None:
            return 1
        left_count = 0
        right_count = 0
        if self.left != None:
            left_count = self.left.node_count()
        if self.right != None:
            right_count = self.right.node_count()
        return left_count + right_count + 1
    
    def get_approved(self): #override
        left_apprv = 0
        right_apprv = 0
        if self.left != None:
            left_apprv = self.left.get_approved()
        if self.right != None:
            right_apprv = self.right.get_approved()    
        return self.approved + left_apprv + right_apprv

    def get_denied(self): #override
        left_deny = 0
        right_deny = 0
        if self.left != None:
            left_deny = self.left.get_denied()
        if self.right != None:
            right_deny = self.right.get_denied()
        return self.denied + left_deny + right_deny
    
    def predict(self, loan):
        if self.field == "class":
            if self.threshold == '1':
                self.approved += 1
                return True
            else:
                self.denied += 1
                return False
        if loan[self.field] <= float(self.threshold):
            return self.left.predict(loan) #recursive case
        if loan[self.field] > float(self.threshold):
            return self.right.predict(loan)
        
        
        
def build_tree(rows, root_idx=0):
    field = rows[root_idx]['field']
    threshold = rows[root_idx]['threshold']
    left_val = int(rows[root_idx]['left'])
    right_val = int(rows[root_idx]['right'])
    left = None
    right = None
    if field != 'class':
        left = build_tree(rows, root_idx = left_val)
        right = build_tree(rows, root_idx = right_val)

    return Node(field, threshold, left, right)


def bias_test(bank, predictor, field, value_override):
    c1 = 0
    c2 = 0
    for loan in bank.loans():
        pred = predictor.predict(loan)
        if field == "race":            
            loan.race = value_override
        if field == "sex":
            loan.sex = value_override
        over_ride = predictor.predict(loan)
        if pred != over_ride:
            c1+=1
        c2 += 1
    return c1/c2
    



    
    
    
    
    
    
    
    
    
    
 
    