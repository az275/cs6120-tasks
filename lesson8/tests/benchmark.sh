#!/bin/sh

# compile, run 5x, compute mean runtime and percentage speedup
run_benchmark() {
    local name=$1
    local src_dir=$2
    local src_file=$3
    local extra_flags=$4

    clang -O1 $extra_flags -I utilities -I $src_dir utilities/polybench.c $src_dir/$src_file -DPOLYBENCH_TIME -o ${name}_time

    mean=$(for i in {1..5}; do ./${name}_time; done | awk '{sum+=$1} END {print sum/NR}')
    echo "$name mean: $mean" >> benchmark_results.txt

    if [[ $name == *_LICM ]]; then
        base_name=${name/_LICM/_baseline}
        base_mean=$(grep "$base_name mean" benchmark_results.txt | awk '{print $3}')
        if [[ -n "$base_mean" ]]; then
            # percentage speedup: ((baseline - LICM) / baseline) * 100
            speedup=$(awk -v b=$base_mean -v l=$mean 'BEGIN {print ((b-l)/b)*100}')
            echo "$name speedup: $speedup%" >> benchmark_results.txt
        fi
    fi
}

# --- Benchmarks ---
run_benchmark "correlation_baseline" "datamining/correlation" "correlation.c"
run_benchmark "correlation_LICM" "datamining/correlation" "correlation.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "covariance_baseline" "datamining/covariance" "covariance.c"
run_benchmark "covariance_LICM" "datamining/covariance" "covariance.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "2mm_baseline" "linear-algebra/kernels/2mm" "2mm.c"
run_benchmark "2mm_LICM" "linear-algebra/kernels/2mm" "2mm.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "3mm_baseline" "linear-algebra/kernels/3mm" "3mm.c"
run_benchmark "3mm_LICM" "linear-algebra/kernels/3mm" "3mm.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "atax_baseline" "linear-algebra/kernels/atax" "atax.c"
run_benchmark "atax_LICM" "linear-algebra/kernels/atax" "atax.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "bicg_baseline" "linear-algebra/kernels/bicg" "bicg.c"
run_benchmark "bicg_LICM" "linear-algebra/kernels/bicg" "bicg.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "doitgen_baseline" "linear-algebra/kernels/doitgen" "doitgen.c"
run_benchmark "doitgen_LICM" "linear-algebra/kernels/doitgen" "doitgen.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "mvt_baseline" "linear-algebra/kernels/mvt" "mvt.c"
run_benchmark "mvt_LICM" "linear-algebra/kernels/mvt" "mvt.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "gemm_baseline" "linear-algebra/blas/gemm" "gemm.c"
run_benchmark "gemm_LICM" "linear-algebra/blas/gemm" "gemm.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "gemver_baseline" "linear-algebra/blas/gemver" "gemver.c"
run_benchmark "gemver_LICM" "linear-algebra/blas/gemver" "gemver.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "gesummv_baseline" "linear-algebra/blas/gesummv" "gesummv.c"
run_benchmark "gesummv_LICM" "linear-algebra/blas/gesummv" "gesummv.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "symm_baseline" "linear-algebra/blas/symm" "symm.c"
run_benchmark "symm_LICM" "linear-algebra/blas/symm" "symm.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "syr2k_baseline" "linear-algebra/blas/syr2k" "syr2k.c"
run_benchmark "syr2k_LICM" "linear-algebra/blas/syr2k" "syr2k.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "syrk_baseline" "linear-algebra/blas/syrk" "syrk.c"
run_benchmark "syrk_LICM" "linear-algebra/blas/syrk" "syrk.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "trmm_baseline" "linear-algebra/blas/trmm" "trmm.c"
run_benchmark "trmm_LICM" "linear-algebra/blas/trmm" "trmm.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "cholesky_baseline" "linear-algebra/solvers/cholesky" "cholesky.c"
run_benchmark "cholesky_LICM" "linear-algebra/solvers/cholesky" "cholesky.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "durbin_baseline" "linear-algebra/solvers/durbin" "durbin.c"
run_benchmark "durbin_LICM" "linear-algebra/solvers/durbin" "durbin.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "gramschmidt_baseline" "linear-algebra/solvers/gramschmidt" "gramschmidt.c"
run_benchmark "gramschmidt_LICM" "linear-algebra/solvers/gramschmidt" "gramschmidt.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "lu_baseline" "linear-algebra/solvers/lu" "lu.c"
run_benchmark "lu_LICM" "linear-algebra/solvers/lu" "lu.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "ludcmp_baseline" "linear-algebra/solvers/ludcmp" "ludcmp.c"
run_benchmark "ludcmp_LICM" "linear-algebra/solvers/ludcmp" "ludcmp.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "trisolv_baseline" "linear-algebra/solvers/trisolv" "trisolv.c"
run_benchmark "trisolv_LICM" "linear-algebra/solvers/trisolv" "trisolv.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "deriche_baseline" "medley/deriche" "deriche.c"
run_benchmark "deriche_LICM" "medley/deriche" "deriche.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "floyd-warshall_baseline" "medley/floyd-warshall" "floyd-warshall.c"
run_benchmark "floyd-warshall_LICM" "medley/floyd-warshall" "floyd-warshall.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "nussinov_baseline" "medley/nussinov" "nussinov.c"
run_benchmark "nussinov_LICM" "medley/nussinov" "nussinov.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "adi_baseline" "stencils/adi" "adi.c"
run_benchmark "adi_LICM" "stencils/adi" "adi.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "fdtd-2d_baseline" "stencils/fdtd-2d" "fdtd-2d.c"
run_benchmark "fdtd-2d_LICM" "stencils/fdtd-2d" "fdtd-2d.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "heat-3d_baseline" "stencils/heat-3d" "heat-3d.c"
run_benchmark "heat-3d_LICM" "stencils/heat-3d" "heat-3d.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "jacobi-1d_baseline" "stencils/jacobi-1d" "jacobi-1d.c"
run_benchmark "jacobi-1d_LICM" "stencils/jacobi-1d" "jacobi-1d.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "jacobi-2d_baseline" "stencils/jacobi-2d" "jacobi-2d.c"
run_benchmark "jacobi-2d_LICM" "stencils/jacobi-2d" "jacobi-2d.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"

run_benchmark "seidel-2d_baseline" "stencils/seidel-2d" "seidel-2d.c"
run_benchmark "seidel-2d_LICM" "stencils/seidel-2d" "seidel-2d.c" "-fpass-plugin=../cs6120-tasks/lesson8/build/src/LICMPass.dylib"
