import discord
import random
from discord.ext import commands

def replacer(s, newstring, index, nofail=False):
    # raise an error if index is outside of the string
    if not nofail and index not in range(len(s)):
        raise ValueError("index outside given string")

    # if not erroring, but the index is still not in the correct range..
    if index < 0:  # add it to the beginning
        return newstring + s
    if index > len(s):  # add it to the end
        return s + newstring

    # insert the new string between "slices" of the original
    return s[:index] + newstring + s[index + 1:]

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def truthordare(self, ctx):
        
        await ctx.send("working on it")
    @commands.command()
    async def hangman(self,ctx):
        words = [
        'sheep', 'cow', 'elephant',
        ]   
        word = random.choice(words)
        await ctx.send(f"Your word is {'_ '*len(word)}")
  
        guessed = word.split(' ')
        game =  True
        ###

        while game:

            msg = await self.bot.wait_for('message', check=...)
            if msg.content == 'q':
              return await ctx.send('goodbye')
            if msg.content == word:
              return await ctx.send(f'You guessed correctly! The word was {word}')
            if msg.content in word:
              newword = word
              guessed.remove(msg.content)
              for k in guessed:
                newword = newword.replace(k, '_ ')

              await ctx.send(f'{msg} is in the word! Here is your revealed word || {newword}')
    
    
def setup(bot):
    bot.add_cog(Fun(bot))
