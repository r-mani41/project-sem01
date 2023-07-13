from texttable import Texttable

tablespace = {}


# function to create table
def create_table(table_name, attributes):
    # checking if table already exists
    if table_name in tablespace:
        print("table already exists! please try to give a new name for your table \n")
        return
    # creating the table
    tablespace[table_name] = {
        "schema": {},
        "row": [],
    }
    table = tablespace[table_name]
    # setting up the column and its datatype for the table
    for column in attributes.split(","):
        col_name, col_datatype = column.split("=")
        table["schema"][col_name] = col_datatype

    print("\n {} table created \n".format(table_name))
    return


# function to insert row to table
def insert_table(table_name, row_data, row_count):
    # checking if table exists
    if table_name not in tablespace:
        print("table does not exists! \n")
        return

    for index in range(row_count):
        row = {}
        col_data = row_data[index].split(",")
        for data in col_data:
            col_name, col_value = data.split("=")

            # checking if column exists in table
            if col_name not in tablespace[table_name]["schema"]:
                print(
                    "column name {} does not exits in table {} \n".format(
                        col_name, table_name
                    )
                )
                return

            # checking if datatype matches against table column schema
            datatype = tablespace[table_name]["schema"][col_name]
            flag = False
            if datatype == "int" and not col_value.isdigit():
                flag = True
            elif datatype == "char" and len(col_value) > 1:
                flag = True
            elif datatype == "bool" and not (
                col_value == "true" or col_value == "false"
            ):
                flag = True

            # checking if datatype error
            if flag:
                print(
                    "datatype for column {} is {}, please check the column value".format(
                        col_name, datatype
                    )
                )
                return

            row[col_name] = col_value

        # inserting row to the table
        tablespace[table_name]["row"].append(row)

    print("inserted {} row to the table {} \n".format(row_count, table_name))
    return


# function to select rows from table
def select_table(table_name, column, exp=None, log_op=None):
    t = Texttable()
    exp_len = len(exp)
    log_op_len = len(log_op)
    column = column.split(",")
    # if * select all columns else choose user specified columns
    if column[0] == "*":
        col_header = tablespace[table_name]["schema"].keys()
    else:
        col_header = column
    t.add_row(col_header)

    # get all rows of the table
    total_rows = tablespace[table_name]["row"]

    for row in total_rows:
        qualified_row = eval_row(row, exp, log_op, exp_len, log_op_len)
        # print("qualified", qualified_row)
        if qualified_row:
            record = row.items()
            temp = []
            for col in record:
                if col[0] in column or column[0] == "*":
                    temp.append(col[1])
            t.add_row(temp)

    print(t.draw())

    return


def eval_row(row_record, exp, log_op, exp_len, log_op_len):
    # print("eval_row", row_record, exp, log_op, exp_len, log_op_len)
    if exp_len == 1:
        return extract_conditional_operator(exp[0], row_record)

    flag = True
    i = 0
    j = 0
    while i < exp_len and j < log_op_len:
        exp_1 = extract_conditional_operator(exp[i], row_record)
        i += 1
        if i < exp_len:
            exp_2 = extract_conditional_operator(exp[i], row_record)
            if eval_expression(exp_1, exp_2, log_op[j]):
                i += 1
                j += 1
            else:
                flag = False
                break

    return flag


def eval_expression(exp_1, exp_2, log_op):
    # print("eval expression", exp_1, exp_2, log_op)
    if log_op == "&":
        if exp_1 and exp_2:
            return True
    elif log_op == "|":
        if exp_1 or exp_2:
            return True

    return False


def extract_conditional_operator(exp, row_record):
    if ">=" in exp:
        cond_exp = ">="
        cond_col, cond_val = exp.split(">=")
    elif "<=" in exp:
        cond_exp = "<="
        cond_col, cond_val = exp.split("<=")
    elif "!=" in exp:
        cond_exp = "!="
        cond_col, cond_val = exp.split("!=")
    elif ">" in exp:
        cond_exp = ">"
        cond_col, cond_val = exp.split(">")
    elif "<" in exp:
        cond_exp = "<"
        cond_col, cond_val = exp.split("<")
    elif "=" in exp:
        cond_exp = "="
        cond_col, cond_val = exp.split("=")
    else:
        print("\n Invalid expression to evaluate where condition!")
        return False
    # print("Inside extract", exp, row_record, cond_exp, cond_val)
    # print("\n")
    return check_expression(cond_val, row_record[cond_col], cond_exp)


def check_expression(cond_val, col_val, cond):
    # print("Inside Check Expression", cond_val, col_val, cond)
    if cond == "=" and col_val == cond_val:
        return True
    elif cond == ">" and col_val > cond_val:
        return True
    elif cond == "<" and col_val < cond_val:
        return True
    elif cond == ">=" and col_val >= cond_val:
        return True
    elif cond == "<=" and col_val <= cond_val:
        return True
    elif cond == "!=" and col_val != cond_val:
        return True

    return False


if __name__ == "__main__":
    while True:
        user_string = input(" query >> ")
        query = user_string.split(" ")
        keyword = query[0]
        # exit from input
        if keyword == "exit":
            break
        table_name = query[1]
        if keyword == "create":
            create_table(table_name, query[2])
        elif keyword == "insert":
            insert_table(table_name, query[2:], len(query[2:]))
        elif keyword == "select":
            cols = query[2]
            query_length = len(query)
            # acting for where condition exists
            start = 4
            logical_operator = []
            expression = []
            # seperating expression and logical operator
            while start < query_length:
                expression.append(query[start])
                start += 1
                if start < query_length:
                    logical_operator.append(query[start])
                start += 1
            select_table(table_name, cols, expression, logical_operator)

    # print(tablespace)
