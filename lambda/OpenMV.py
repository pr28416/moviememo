import requests
from datetime import datetime as dt

class OpenMV:
    @staticmethod
    def _int_to_roman(num):
        val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
        roman_num = ''
        i = 0
        while num > 0:
            for _ in range(num // val[i]):
                roman_num += syb[i]
                num -= val[i]
            i += 1
        return roman_num

    @staticmethod
    def _approxJSON(mov, year=None, mov_list=None, skip_recurse=True, index=0):
        if skip_recurse:
            return OpenMV._approxJSON(None, year, mov.lower().split(" "), False)
        else:
            if index >= len(mov_list):
                approx_year_delta = [0,1,-1,2,-2]
                for aDelta in approx_year_delta:
                    try:
                        req = requests.get(f"http://www.omdbapi.com/?i=tt3896198&apikey=4a55b13&t={'+'.join(mov_list)}{'&y=%s' % (int(year)+aDelta) if year is not None else ''}")
                        if 'Error' not in req.json(): return req
                    except: continue
            else:
                req = OpenMV._approxJSON(None, year, mov_list, False, index+1)
                if req: return req
                orig = mov_list[index]
                try:
                    mov_list[index] = OpenMV._int_to_roman(int(mov_list[index]))
                    req = OpenMV._approxJSON(None, year, mov_list, False, index+1)
                    if req: return req
                except: pass
                mov_list[index] = orig

    @staticmethod
    def getMovie(movie, year=None):
        mov = OpenMV._approxJSON(movie, year)
        return (f"An error was encountered when retrieving the movie. The given movie or TV show may not exist or the year, if provided, may be incorrect. The given movie title was: {movie}", True) if mov is None else (mov, False)

    @staticmethod
    def fullDescribe(movie, year=None):
        mov, failed = OpenMV.getMovie(movie, year)
        if failed: return mov
        m = mov.json()
        actors = mov.json()["Actors"].split(", ")
        actors = "None" if not len(actors) else \
                    actors[0] if len(actors) == 1 else \
                    ", ".join(actors[:-1]) + f", and {actors[-1]}"
                    
        return f"{m['Title']} is a {m['Type']} that was released on {dt.strftime(dt.strptime(m['Released'], '%d %b %Y'), '%B %m, %Y')} in {m['Country']} and was rated {m['imdbRating']} on IMDB. Some actors include {actors}. {m['Plot']}"

    @staticmethod
    def whoActedInMovie(movie, year=None):
        mov, failed = OpenMV.getMovie(movie, year)
        if failed: return mov
        m = mov.json()
        actors = mov.json()["Actors"].split(", ")
        actors = "None" if not len(actors) else \
                    actors[0] if len(actors) == 1 else \
                    ", ".join(actors[:-1]) + f", and {actors[-1]}"
        return f"{actors} acted in the {m['Type']} {m['Title']}."

    @staticmethod
    def whatIsMoviePlot(movie, year=None):
        mov, failed = OpenMV.getMovie(movie, year)
        if failed: return mov
        m = mov.json()
        return f"The following is the plot of {m['Title']}: {m['Plot']}"

    @staticmethod
    def howWasMovieRated(movie, year=None):
        mov, failed = OpenMV.getMovie(movie, year)
        if failed: return mov
        m = mov.json()
        ratings = []
        for rating in m['Ratings']:
            prefix = f"{rating['Source']} gave a rating of"
            suffix = rating["Value"][:-1] + " percent" if "%" in rating["Value"] else " out of ".join(rating["Value"].split("/"))
            ratings.append(f"{prefix} {suffix}.")
        return f"The following are some ratings for the {m['Type']} {m['Title']}: {' '.join(ratings)}"