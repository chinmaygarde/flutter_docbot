#!/usr/bin/env python3

import argparse
import datetime
import errno
import os
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urljoin
import xml.etree.ElementTree as et

def GetRepoSHA(repository):
  version = subprocess.check_output([
    'git',
    '-C',
    repository,
    'rev-parse',
    'HEAD',
  ])

  return version.strip().decode("utf-8")

def TempLocation():
  temp_directory = tempfile.mkdtemp()
  assert os.path.exists(temp_directory)
  return os.path.join(temp_directory, 'repository')

def CloneRepo(repo_location, repo):
  subprocess.check_call([
    'git',
    'clone',
    '--depth',
    '1',
    repo,
    repo_location
  ])
  return repo_location

def GenerateDocumentation(repo, repo_sha):
  engine_location = os.path.join(os.path.abspath(repo), 'engine/src/flutter')
  doxygen_location = os.path.join(engine_location, 'docs/doxygen')

  with open(os.path.join(engine_location, "Doxyfile"), "rb") as f:
    doxy_content = f.read() + b"\nSITEMAP_URL=https://engine.chinmaygarde.com\nPROJECT_NAME=\"Flutter Engine Uber Docs\"\nPROJECT_BRIEF=\"Docs for the entire Flutter Engine repo.\"\n"

  # Use Doxygen to create the HTML documentation.
  subprocess.run([
      'doxygen',
      '-',
    ],
    cwd=engine_location,
    input=doxy_content,
    check=True,
  )
  doc_location = os.path.join(doxygen_location, 'html')
  assert os.path.exists(doc_location)



  # Use doxygen2docset to create a docset from the generated HTML documentation.
  docset_location = os.path.join(doxygen_location, 'docset')
  subprocess.check_call([
    'doxygen2docset',
    '--doxygen',
    doc_location,
    '--docset',
    docset_location,
  ])
  assert os.path.exists(docset_location)


  # Create a tarball from the generated Dash docset.
  docset_tar_location = os.path.join(doxygen_location, 'html/FlutterEngine.tgz')
  subprocess.check_call([
    'tar',
    '-czvf',
    docset_tar_location,
    '.'
  ], cwd=docset_location)
  assert os.path.exists(docset_tar_location)


  # Generate an XML file that species the updated feed location.
  feed_file = os.path.join(doxygen_location, 'html/docset.xml')
  with open(feed_file, "w") as text_file:
    text_file.write("<entry><version>%s</version><url>https://engine.chinmaygarde.com/FlutterEngine.tgz</url></entry>" % repo_sha)
  os.path.exists(feed_file)
  feed_file2 = os.path.join(doxygen_location, 'html/FlutterEngine.xml')
  with open(feed_file2, "w") as text_file:
    text_file.write("<entry><version>%s</version><url>https://engine.chinmaygarde.com/FlutterEngine.tgz</url></entry>" % repo_sha)
  os.path.exists(feed_file2)

  return doc_location

def CopyDirectory(source, destination):
  shutil.copytree(source, destination, symlinks=True)

def RemoveDirectory(source):
  shutil.rmtree(source)

def main():
  parser = argparse.ArgumentParser()

  parser.add_argument('--repo',
      help='The repo to pull from to get the Doxygen source',
      required=True)
  parser.add_argument('--doc-destination',
      help='The location to place the generated documentation.',
      required=True)

  args = parser.parse_args();
  repo_location = CloneRepo(TempLocation(), args.repo)
  repo_sha = GetRepoSHA(repo_location)
  doc_destination = args.doc_destination

  assert not os.path.exists(doc_destination)

  doc_location = GenerateDocumentation(repo_location, repo_sha)

  CopyDirectory(doc_location, doc_destination)

  RemoveDirectory(doc_location)
  RemoveDirectory(repo_location)

  return 0

if __name__ == '__main__':
  sys.exit(main())
