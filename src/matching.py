def is_match(c1, c2):
    x1,y1,d1 = c1
    x2,y2,d2 = c2

    tol = max(6, 0.2*d1)

    return (abs(x1-x2)<tol and abs(y1-y2)<tol and abs(d1-d2)<tol)


def match_craters(all_craters):
    final = []

    for c in all_craters[0]:
        matches = 1

        for others in all_craters[1:]:
            for c2 in others:
                if is_match(c, c2):
                    matches += 1
                    break

        if len(all_craters) == 1 or matches >= 2:
            final.append(c)

    return final
