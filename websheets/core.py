def collect_import_errors(result):
    errors={}
    if result.has_errors():
        if result.base_errors:
            errors[1]=["Internal base errors"]
        
        for rownum, errs in result.row_errors():
            if rownum not in errors: errors[rownum]=[]
            for e in errs:
                if hasattr(e.error, '__iter__'):
                    errors[rownum].extend(str(p) for p in e.error)
                else:
                    errors[rownum].append(str(e.error))
    if result.has_validation_errors():
        for ir in result.invalid_rows:
            rownum=ir.number
            if rownum not in errors: errors[rownum]=[]
            for ek,ev in ir.error.message_dict.items():
                for em in ev:
                    errors[rownum].append("%s: %s" % (ek,em))
                    
    return errors