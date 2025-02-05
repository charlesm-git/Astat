[app]
title = Astat
package.name = com.cmareau.astat
package.domain = com.cmareau.astat
source.dir = .
version = 1.0
requirements = python3, kivy, kivymd2, sqlalchemy, matplotlib, numpy, kiwisolver
orientation = portrait 

[android]
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE 
android.api = 34
android.minapi = 21
android.ndk = 25b
android.sdk = 34
android.arch = arm64-v8a
android.requirements = libpng, freetype, zlib