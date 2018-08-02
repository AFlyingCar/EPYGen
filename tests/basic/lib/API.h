#ifndef API_H
#define API_H

#ifdef EXPORT
#ifdef _WIN32
#define API __declspec(dllexport)
#else
#define API
#endif
#else
#ifdef _WIN32
#define API __declspec(dllimport)
#else
#define API
#endif
#endif

#endif
