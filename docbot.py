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
  subprocess.check_call([
    'doxygen',
  ], cwd=repo)
  doc_location = os.path.join(repo, 'docs', 'doxygen', 'html')
  assert os.path.exists(doc_location)
  docset_location = os.path.join(repo, 'docs', 'doxygen', 'docset')
  subprocess.check_call([
    'doxygen2docset',
    '--doxygen',
    doc_location,
    '--docset',
    docset_location,
  ])
  assert os.path.exists(docset_location)
  docset_tar_location = os.path.join(repo, 'docs', 'doxygen', 'html', 'FlutterEngine.tgz')
  subprocess.check_call([
    'tar',
    '-czvf',
    docset_tar_location,
    '.'
  ], cwd=docset_location)
  assert os.path.exists(docset_tar_location)
  feed_file = os.path.join(repo, 'docs', 'doxygen', 'html', 'docset.xml')
  with open(feed_file, "w") as text_file:
    text_file.write("<entry><version>%s</version><url>https://public.chinmaygarde.com/docs/flutter_engine/FlutterEngine.tgz</url></entry>" % repo_sha)
  os.path.exists(feed_file)
  feed_file2 = os.path.join(repo, 'docs', 'doxygen', 'html', 'FlutterEngine.xml')
  with open(feed_file2, "w") as text_file:
    text_file.write("<entry><version>%s</version><url>https://public.chinmaygarde.com/docs/flutter_engine/FlutterEngine.tgz</url></entry>" % repo_sha)
  os.path.exists(feed_file2)
  return doc_location

def UpdateSylink(target, link_name):
  try:
    os.symlink(target, link_name)
  except (OSError, e):
    if e.errno == errno.EEXIST:
      os.remove(link_name)
      os.symlink(target, link_name)
    else:
      raise e

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
  CloneRepo(os.path.join(repo_location, "third_party", "skia"), "https://github.com/google/skia.git")
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
