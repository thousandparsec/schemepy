# -*- Ruby -*-

#########################################
# Document tasks
#########################################
namespace :doc do
  def doc_output(doc)
    File.dirname(doc) + '/../html/' + File.basename(doc, ".rst") + ".html"
  end

  FileList['doc/src/*.rst'].each do |doc|
    output = doc_output(doc)
    file output => doc do
      sh "doc/src/compile-doc.py #{doc} > #{output}"
    end
    task :generate => output
  end

  desc "Generate HTML document"
  task :generate
end
task :doc => 'doc:generate'



#########################################
# Test tasks
#########################################
namespace :test do
  Backends = [:guile, :pyscheme]

  Backends.each do |backend|
    desc "Run test cases on #{backend} backend"
    task backend do
      ENV['TEST_MODULE'] = backend.to_s
      sh "py.test --tb=short tests"
    end
  end

  desc "Run test cases on all backends"
  task :all => Backends
end
task :test => 'test:all'



task :default => :test
