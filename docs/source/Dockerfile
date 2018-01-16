FROM haskell:8.0

# install latex packages
RUN apt-get update -y && apt-get install -y apt-transport-https

ENV PANDOC_VERSION "1.19.2.1"

# install pandoc
RUN cabal update && cabal install pandoc-${PANDOC_VERSION}

WORKDIR /source

ENTRYPOINT ["/root/.cabal/bin/pandoc"]

CMD ["--help"]