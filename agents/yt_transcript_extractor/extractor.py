from langchain_community.document_loaders import YoutubeLoader


def load_transcript(url):
    transcipt_loader = YoutubeLoader.from_youtube_url(
    url, 
    add_video_info=False
    )


    return transcipt_loader.load()

if __name__ == '__main__':
    print(load_transcript("https://www.youtube.com/watch?v=REIlo713ulU"))
