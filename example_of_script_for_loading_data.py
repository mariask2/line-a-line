import extract_tmx_to_fastalign_format

if __name__ == "__main__":
    files = ["projects/public_authority_texts_de_sv/tmx/257.de-sv.tmx",\
         "projects/public_authority_texts_de_sv/tmx/258.de-sv.tmx",\
         "projects/public_authority_texts_de_sv/tmx/259.de-sv.tmx"]
    
    name = "labour_market_social_security"
    lang2_path = 'alignedspaces/wiki.multi.sv.vec.txt'
    lang1_path = 'alignedspaces/wiki.multi.de.vec.txt'
    
    lang2 = "sv"
    lang1 = "de"
    
    lang2_stopword_name = 'swedish'
    lang1_stopword_name = 'german'
    
    extract_tmx_to_fastalign_format.run_extract_and_convert(name, files, lang1, lang2, lang1_path, lang2_path, lang1_stopword_name, lang2_stopword_name)
