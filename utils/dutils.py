import json

def jsonwriter(file1, data1):
    file1.truncate(0)
    file1.seek(0)
    file1.write(json.dumps(data1, indent=4))




async def paginate(ctx, embeds:list):

    current = 0
    msg = await ctx.send(embed=embeds[0])
    await msg.add_reaction("<:left:898911001158750229>")
    await msg.add_reaction("<:right:898910929264214076>")
    await msg.add_reaction("<:stop:898911046918627379>")

    
    def check(e, u):
            return u == ctx.author and e.message == msg
        
    e, u = await ctx.bot.wait_for('reaction_add', check=check)
    
    while str(e.emoji) != "<:stop:898911046918627379>":
        name = str(e.emoji)
        if name == "<:left:898911001158750229>":
            current -=1
            
        elif name == "<:right:898910929264214076>":
            current +=1
        
        
        await msg.remove_reaction(member=ctx.author, emoji=e.emoji)
        await msg.edit(embed=embeds[current])
        
        e, u = await ctx.bot.wait_for('reaction_add', check=check)
        
    else:
        return await msg.clear_reactions()