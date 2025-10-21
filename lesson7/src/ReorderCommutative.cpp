#include "llvm/Pass.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/Module.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/FileSystem.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

namespace {

struct SkeletonPass : public PassInfoMixin<SkeletonPass> {
    void printIR(Module &M) {
        std::error_code err;
        raw_fd_ostream outFile("reorder_IR.txt", err, sys::fs::OF_Text);
        if (err) {
            errs() << "Error opening file: " << err.message() << "\n";
            return;
        }

        for (auto &F : M.functions()) {
            F.print(outFile);
        }
    }

    PreservedAnalyses run(Module &M, ModuleAnalysisManager &AM) {
        for (auto &F : M) {
            for (auto &B : F) {
                for (auto &I : B) {
                    if (auto *op = dyn_cast<BinaryOperator>(&I)) {
                        if (!Instruction::isCommutative(op->getOpcode())) {
                            continue;
                        }

                        Value *left = op->getOperand(0);
                        Value *right = op->getOperand(1);

                        // swap so that constants come first
                        if (!isa<ConstantInt>(left) && isa<ConstantInt>(right)) {
                            op->setOperand(0, right);
                            op->setOperand(1, left);
                        }
                    }
                }
            }
        }
        printIR(M);
        return PreservedAnalyses::none();
    }
};

}

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
    return {
        .APIVersion = LLVM_PLUGIN_API_VERSION,
        .PluginName = "Skeleton pass",
        .PluginVersion = "v0.1",
        .RegisterPassBuilderCallbacks = [](PassBuilder &PB) {
            PB.registerPipelineStartEPCallback(
                [](ModulePassManager &MPM, OptimizationLevel Level) {
                    MPM.addPass(SkeletonPass());
                });
        }
    };
}
