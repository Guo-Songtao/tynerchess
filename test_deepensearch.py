import position as p

def test_capturesOnly():
    pos = p.Position()
    pos.init()
    
    allc = pos.allMoves(True)
    allm = pos.allMoves()
    print(allm, len(allm))
    print(allc, len(allc))
    

if __name__== "__main__":
    test_capturesOnly()