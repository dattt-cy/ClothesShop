import polib

# Compile Japanese
po_ja = polib.pofile(r'C:\Users\ADMIN\Desktop\BeeShop\locale\ja\LC_MESSAGES\django.po')
po_ja.save_as_mofile(r'C:\Users\ADMIN\Desktop\BeeShop\locale\ja\LC_MESSAGES\django.mo')

# Compile Vietnamese
po_vi = polib.pofile(r'C:\Users\ADMIN\Desktop\BeeShop\locale\vi\LC_MESSAGES\django.po')
po_vi.save_as_mofile(r'C:\Users\ADMIN\Desktop\BeeShop\locale\vi\LC_MESSAGES\django.mo')

print("Translation files compiled successfully!")

