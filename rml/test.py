import rbnf.zero as ze


def success(result: ze.ResultDescription):
    return len(result.tokens) <= result.state.end_index


ze_exp = ze.compile('import rml.rml.[*]', use='ModuleDef')

assert success(ze_exp.match("""
module S where
let (x, y) = 1
"""))

assert not success(ze_exp.match("""
module S where
    let (x, y) = 1
  in x = y
"""))

assert success(ze_exp.match("""
module S where
    let (x, y) = "s\\""
    in x + y
"""))

assert not success(ze_exp.match("""
module S where
    type S = 
    | S Int
  | S Int * (A of 'a)
    
"""))

# ze_exp = ze.compile('import rml.rml.[*]', use='Stmts')

assert not success(ze_exp.match("""
module S where
    for x in f yield 
   1  
"""))

assert not success(ze_exp.match("""
module S where
    for x in f yield 
    1  
"""))

assert success(ze_exp.match("""
module S where
    for x in f yield 
       1  
"""))
